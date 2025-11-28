from __future__ import annotations

DOMAIN = "elecq_ocpp"

SIGNAL_STATE_UPDATED = "elecq_ocpp_state_updated"

# Config keys
CONF_PORT = "port"
CONF_ID_TOKEN = "id_token"
CONF_EVSE_ID = "evse_id"
CONF_CONNECTOR_ID = "connector_id"

# Default values
DEFAULT_PORT = 9006
DEFAULT_EVSE_ID = 1
DEFAULT_CONNECTOR_ID = 1
DEFAULT_ID_TOKEN = "ElecqAutoStart"
