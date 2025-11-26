from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import websockets
from websockets.server import WebSocketServer
from websockets.exceptions import ConnectionClosed

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from ocpp.routing import on
from ocpp.v201 import ChargePoint as OcppChargePointBase
from ocpp.v201 import call, call_result
from ocpp.v201.enums import (
    RegistrationStatusEnumType,
    RequestStartStopStatusEnumType,
)

from .const import SIGNAL_STATE_UPDATED

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CENTRAL STATE MODEL
# ---------------------------------------------------------------------------


@dataclass
class ElecqChargerState:
    """Live state from Elecq charger."""

    # Instantaneous & smoothed power
    power_kw: Optional[float] = None
    power_kw_smoothed: Optional[float] = None

    # Cumulative meter total (from Energy.Active.Import.Register)
    energy_kwh: Optional[float] = None

    # Session energy and timing
    session_energy_kwh: Optional[float] = None
    session_start: Optional[datetime] = None
    session_start_meter_kwh: Optional[float] = None
    session_event_type: Optional[str] = None
    session_trigger_reason: Optional[str] = None

    # Status flags
    plugged_in: bool = False
    charging: bool = False

    # Remote stop tracking (optional convenience)
    remote_stop_requested: bool = False

    # OCPP transaction fields
    transaction_id: Optional[str] = None
    last_status: Optional[str] = None  # StatusNotification.connector_status
    last_charging_state: Optional[str] = None  # TransactionEvent.charging_state

    # Raw last TE payload for diagnostics
    last_transaction_info: Optional[dict[str, Any]] = None
    last_meter_value: Optional[list[dict[str, Any]]] = None

    last_update: Optional[datetime] = None


# ---------------------------------------------------------------------------
# MANAGER
# ---------------------------------------------------------------------------


class ElecqOcppManager:
    """Manager running OCPP server & storing charger state."""

    def __init__(
        self,
        hass: HomeAssistant,
        port: int,
        id_token: str,
        evse_id: int,
        connector_id: int,
    ) -> None:
        self.hass = hass
        self.port = port
        self.id_token = id_token
        self.evse_id = evse_id
        self.connector_id = connector_id

        self._cp: Optional["ElecqChargePoint"] = None
        self._server: Optional[WebSocketServer] = None

        self.state = ElecqChargerState()

        # Rolling window for smoothed power (kW)
        self._power_window: list[float] = []
        self._max_power_samples: int = 5

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _notify(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_STATE_UPDATED)

    def _update_power_smoothing(self, power_kw: float) -> None:
        self._power_window.append(power_kw)
        if len(self._power_window) > self._max_power_samples:
            self._power_window.pop(0)
        self.state.power_kw_smoothed = sum(self._power_window) / len(self._power_window)

    def _update_session_energy(self, total_kwh: float) -> None:
        st = self.state
        if st.session_start is None:
            return

        if st.session_start_meter_kwh is None:
            st.session_start_meter_kwh = total_kwh

        st.session_energy_kwh = max(0.0, total_kwh - st.session_start_meter_kwh)

    # ------------------------------------------------------------------
    # OCPP meter value parsing
    # ------------------------------------------------------------------
    def update_meter_values(self, meter_value: list[dict[str, Any]]) -> None:
        """Parse meterValue[] from TransactionEvent."""
        st = self.state

        power_kw = st.power_kw
        total_kwh = st.energy_kwh

        for mv in meter_value:
            # python-ocpp v201 uses 'sampled_value'
            for sv in mv.get("sampled_value", []):
                measurand = sv.get("measurand")
                val_raw = sv.get("value")
                uom = sv.get("unit_of_measure", {}) or {}
                unit = uom.get("unit")
                mult = uom.get("multiplier", 0) or 0

                try:
                    value = float(val_raw) * (10**mult)
                except (TypeError, ValueError):
                    continue

                if measurand == "Power.Active.Import":
                    if unit == "W":
                        power_kw = value / 1000.0
                    else:
                        power_kw = value

                elif measurand == "Energy.Active.Import.Register":
                    total_kwh = value

        st.power_kw = power_kw
        if power_kw is not None:
            self._update_power_smoothing(power_kw)

        st.energy_kwh = total_kwh
        if total_kwh is not None:
            self._update_session_energy(total_kwh)

        st.last_meter_value = meter_value
        st.last_update = datetime.now(timezone.utc)
        self._notify()

    # ------------------------------------------------------------------
    # TransactionEvent handling
    # ------------------------------------------------------------------
    def update_transaction_event(
        self,
        event_type: str,
        trigger_reason: str | None,
        transaction_info: dict[str, Any] | None,
        meter_value: list[dict[str, Any]] | None,
    ) -> None:
        """Handle TransactionEvent from charger."""
        st = self.state

        st.session_event_type = event_type
        st.session_trigger_reason = trigger_reason
        st.last_transaction_info = transaction_info

        # 1) Meter values (power / energy)
        if meter_value:
            self.update_meter_values(meter_value)

        # 2) Transaction info (charging_state, transaction_id, stoppedReason)
        if transaction_info:
            # python-ocpp uses snake_case; be defensive and accept camelCase too
            charging_state = (
                transaction_info.get("charging_state")
                or transaction_info.get("chargingState")
            )
            transaction_id = (
                transaction_info.get("transaction_id")
                or transaction_info.get("transactionId")
            )

            stopped_reason = (
                transaction_info.get("stopped_reason")
                or transaction_info.get("stoppedReason")
            )

            # Handle EV unplug explicitly via stoppedReason
            if stopped_reason == "EVDisconnected":
                _LOGGER.info(
                    "EV disconnected (stoppedReason=EVDisconnected). "
                    "Marking unplugged and clearing session."
                )
                st.plugged_in = False
                st.charging = False
                st.transaction_id = None
                st.last_charging_state = "Idle"
                st.remote_stop_requested = False
                st.session_start = None
                st.session_start_meter_kwh = None
                st.session_energy_kwh = st.session_energy_kwh  # keep last
                st.last_update = datetime.now(timezone.utc)
                self._notify()
                return

            st.last_charging_state = charging_state
            st.transaction_id = transaction_id

            # Derive "charging" from charging_state
            if charging_state == "Charging":
                if st.remote_stop_requested:
                    _LOGGER.info(
                        "Charger reports Charging but remote stop requested; "
                        "keeping charging=False."
                    )
                    st.charging = False
                else:
                    st.charging = True
            elif charging_state in ("Idle", "Finished", "SuspendedEV", "SuspendedEVSE"):
                st.charging = False

            # IMPORTANT: do not force plugged_in=True here.
            # Elecq continues sending TransactionEvent updates after unplug;
            # we rely on StatusNotification and EVDisconnected to clear plugged_in.

        # 3) Session lifecycle
        if event_type == "Started":
            st.session_start = datetime.now(timezone.utc)
            st.session_start_meter_kwh = st.energy_kwh
            st.session_energy_kwh = 0.0
            st.remote_stop_requested = False
        elif event_type in ("Ended", "Stopped"):
            # Transaction ended for some reason (could be EVDisconnected or other);
            # EVDisconnected path above already cleared plugged_in if applicable.
            st.session_start = None
            st.session_start_meter_kwh = None
            st.remote_stop_requested = False
            st.charging = False

        st.last_update = datetime.now(timezone.utc)
        self._notify()

    # ------------------------------------------------------------------
    # Public API for entities (start/stop charging)
    # ------------------------------------------------------------------
    @property
    def is_available(self) -> bool:
        return self._cp is not None

    async def async_request_start(self) -> bool:
        """Send RequestStartTransaction to charger."""
        if self._cp is None:
            _LOGGER.warning("Cannot start transaction: no charger connected.")
            return False

        request = call.RequestStartTransaction(
            evse_id=self.evse_id,
            id_token={"idToken": self.id_token, "type": "Local"},
            remote_start_id=int(datetime.now().timestamp()),
        )

        _LOGGER.info("Sending RequestStartTransaction: %s", request)

        try:
            response = await self._cp.call(request)
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Error sending RequestStartTransaction: %s", err)
            return False

        _LOGGER.info("RequestStartTransaction response: %s", response)

        ok = (
            getattr(response, "status", None)
            == RequestStartStopStatusEnumType.accepted
        )

        if ok:
            # Clear any previous remote stop request; TE will set charging
            self.state.remote_stop_requested = False
            self._notify()

        return ok

    async def async_request_stop(self) -> bool:
        """Send RequestStopTransaction to charger."""
        st = self.state

        if self._cp is None or not st.transaction_id:
            _LOGGER.warning(
                "Cannot stop transaction: no active transaction_id or CP."
            )
            return False

        request = call.RequestStopTransaction(
            transaction_id=st.transaction_id,
        )

        _LOGGER.info("Sending RequestStopTransaction: %s", request)

        try:
            response = await self._cp.call(request)
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Error sending RequestStopTransaction: %s", err)
            return False

        _LOGGER.info("RequestStopTransaction response: %s", response)

        ok = (
            getattr(response, "status", None)
            == RequestStartStopStatusEnumType.accepted
        )

        if ok:
            # Mark that we requested a stop; treat as "not charging"
            st.remote_stop_requested = True
            st.charging = False
            self._notify()

        return ok

    # ------------------------------------------------------------------
    # WebSocket server lifecycle
    # ------------------------------------------------------------------
    async def async_start_server(self) -> None:
        """Start OCPP 2.0.1 WebSocket server."""

        async def _on_connect(websocket):
            req = getattr(websocket, "request", None)

            # Enforce OCPP 2.0.1 subprotocol
            if websocket.subprotocol != "ocpp2.0.1":
                _LOGGER.warning(
                    "Client did not negotiate ocpp2.0.1 (got %s) - closing.",
                    websocket.subprotocol,
                )
                await websocket.close()
                return

            path = req.path if req is not None else "/"
            cp_id = path.strip("/") or "unknown"

            _LOGGER.info("Elecq OCPP: new connection id=%s path=%s", cp_id, path)

            cp = ElecqChargePoint(cp_id, websocket, self)
            self._cp = cp

            try:
                await cp.start()
            except ConnectionClosed:
                _LOGGER.info("Elecq OCPP: connection closed for %s", cp_id)
            finally:
                # Mark offline
                st = self.state
                st.charging = False
                st.plugged_in = False
                st.transaction_id = None
                st.last_charging_state = None
                st.last_status = "Disconnected"
                st.remote_stop_requested = False
                st.last_update = datetime.now(timezone.utc)
                self._notify()

        self._server = await websockets.serve(
            _on_connect,
            host="0.0.0.0",
            port=self.port,
            subprotocols=["ocpp2.0.1"],
        )

        _LOGGER.info(
            "Elecq OCPP 2.0.1 server listening on 0.0.0.0:%s",
            self.port,
        )

    async def async_stop_server(self) -> None:
        """Stop the WebSocket server."""
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            _LOGGER.info("Elecq OCPP server stopped.")


# ---------------------------------------------------------------------------
# CHARGEPOINT IMPLEMENTATION
# ---------------------------------------------------------------------------


class ElecqChargePoint(OcppChargePointBase):
    """OCPP 2.0.1 ChargePoint handlers."""

    def __init__(self, cp_id: str, websocket, manager: ElecqOcppManager) -> None:
        super().__init__(cp_id, websocket)
        self._manager = manager

    @on("BootNotification")
    async def on_boot(self, charging_station, reason, **kwargs):
        _LOGGER.info(
            "BootNotification: model=%s, vendor=%s, reason=%s",
            charging_station.get("model"),
            charging_station.get("vendor_name")
            or charging_station.get("vendorName"),
            reason,
        )
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).isoformat(),
            interval=60,
            status=RegistrationStatusEnumType.accepted,
        )

    @on("Heartbeat")
    async def on_heartbeat(self, **kwargs):
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).isoformat(),
        )

    @on("StatusNotification")
    async def on_status(
        self,
        timestamp,
        evse_id,
        connector_id,
        connector_status,
        **kwargs,
    ):
        """Handle connector status changes from the charger."""
        st = self._manager.state

        status_upper = (connector_status or "").upper()

        # Store raw status so we can expose it as a sensor
        st.last_status = connector_status

        # Plugged-in detection based primarily on StatusNotification:
        #   Available, Faulted -> no EV connected
        #   Everything else (Occupied, Preparing, Charging, Suspended*, etc.) -> EV connected
        if status_upper in ("AVAILABLE", "FAULTED"):
            st.plugged_in = False
        else:
            st.plugged_in = True

        # Charging detection:
        # Prefer TransactionEvent.charging_state if we have it,
        # and don't override a remote stop request.
        if st.last_charging_state is not None:
            st.charging = (
                st.last_charging_state == "Charging"
                and not st.remote_stop_requested
            )
        else:
            st.charging = (
                status_upper == "CHARGING"
                and not st.remote_stop_requested
            )

        st.last_update = datetime.now(timezone.utc)
        self._manager._notify()

        return call_result.StatusNotification()

    @on("TransactionEvent")
    async def on_transaction_event(
        self,
        event_type,
        timestamp,
        trigger_reason,
        seq_no,
        transaction_info,
        evse=None,
        id_token=None,
        meter_value=None,
        **kwargs,
    ):
        _LOGGER.debug(
            "TransactionEvent: event_type=%s trigger_reason=%s seq_no=%s "
            "transaction_info=%s meter_value=%s",
            event_type,
            trigger_reason,
            seq_no,
            transaction_info,
            meter_value,
        )

        self._manager.update_transaction_event(
            event_type=event_type,
            trigger_reason=trigger_reason,
            transaction_info=transaction_info,
            meter_value=meter_value,
        )

        return call_result.TransactionEvent()
