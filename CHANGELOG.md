# Changelog – Elecq AU101 OCPP Integration

## v1.0.0 – Initial Release
- Full OCPP 2.0.1 WebSocket server embedded in Home Assistant
- Real-time charger status updates
- EV plugged-in detection
- Accurate charging state (`Charging`, `EVConnected`, `SuspendedEV`, `Idle`)
- Power & energy monitoring (instant + smoothed)
- Remote start/stop charging via OCPP commands
- Safe switch behavior (grey-out while awaiting charger)
- Session energy tracking
- Status, binary sensor, and switch entities created
- Fully local processing (no cloud)
- Added README, info.md, badges, and integration icons
