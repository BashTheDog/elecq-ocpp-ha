DOMAIN = "elecq_ocpp"

PLATFORMS: list[str] = ["sensor", "binary_sensor", "switch"]

CONF_PORT = "port"
CONF_ID_TOKEN = "id_token"
CONF_EVSE_ID = "evse_id"
CONF_CONNECTOR_ID = "connector_id"

DEFAULT_PORT = 9006
DEFAULT_ID_TOKEN = "ElecqAutoStart"
DEFAULT_EVSE_ID = 1
DEFAULT_CONNECTOR_ID = 1

SIGNAL_STATE_UPDATED = "elecq_ocpp_state_updated"
