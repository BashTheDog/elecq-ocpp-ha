# Elecq AU101 OCPP – Home Assistant Custom Integration

![Elecq OCPP Badge](https://raw.githubusercontent.com/BashTheDog/elecq-ocpp-ha/main/assets/elecq_badge_square.png)

[![GitHub Release](https://img.shields.io/github/v/release/BashTheDog/elecq-ocpp-ha?style=for-the-badge)](https://github.com/BashTheDog/elecq-ocpp-ha/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue.svg?style=for-the-badge)](https://hacs.xyz/)
[![GitHub Stars](https://img.shields.io/github/stars/BashTheDog/elecq-ocpp-ha?style=for-the-badge)](https://github.com/BashTheDog/elecq-ocpp-ha/stargazers)

---

# ⚡ Elecq AU101 OCPP Integration

A Home Assistant integration for the **Elecq AU101** EV Charger using an embedded **OCPP 2.0.1 WebSocket server**.

This integration provides:

- Real-time **charger status**
- EV **plugged-in** state
- True **charging state** (`Charging`, `SuspendedEV`, `Idle`, etc.)
- **Start/Stop charging** via OCPP
- Accurate power + energy metrics
- Grey-out switch behavior while waiting on charger responses
- Fully local operation — no cloud

---

# 🖼 Integration Logo

![Integration Logo](https://raw.githubusercontent.com/BashTheDog/elecq-ocpp-ha/main/assets/elecq_badge_square.png)

---

# 🚀 Features

### 🟢 Charger Status
- Available / Occupied / Faulted / Unavailable

### 🔌 EV Plug Detection
- Detects plug/unplug instantly  
- Uses `stoppedReason: EVDisconnected` to confirm unplug

### 🔋 Charging State
- Charging  
- EVConnected  
- SuspendedEV → **Suspended by EV (possibly full)**  
- Idle / Finished  

### ⚡ Energy Monitoring
- Total Energy (kWh)
- Session Energy
- Real-time Power (kW)
- Smoothed average Power

### 🆘 Smart Charging Switch
- State reflects **actual charger**  
- Greyed-out while awaiting OCPP response  
- Rejects start/stop cleanly when EV full or unplugged  

---

# 📦 Installation

## Option A — HACS (Custom)

1. Go to **HACS → Integrations**
2. Select **Custom repositories**
3. Add:

   ```
   https://github.com/BashTheDog/elecq-ocpp-ha
   ```

4. Category: **Integration**
5. Install & restart Home Assistant

---

## Option B — Manual Installation

Copy the folder:

```
custom_components/elecq_ocpp
```

into:

```
<config>/custom_components/elecq_ocpp/
```

Restart Home Assistant.

---

# 🔧 Configuration

Go to **Settings → Devices & Services → Add Integration → Elecq OCPP**

| Field | Meaning |
|-------|---------|
| **Port** | WebSocket server port (default `9006`) |
| **ID Token** | Token used in RequestStartTransaction |
| **EVSE ID** | Usually `1` |
| **Connector ID** | Usually `1` |

---

# 🔗 Elecq Charger Setup

Set this in the Elecq app:

```
ws://<your-home-assistant-ip>:9006/AU101B2G00127D
```

OCPP version: **2.0.1**

---

# 🧩 Entities

### Sensors
- `sensor.elecq_au101_status`
- `sensor.elecq_au101_charging_state`
- `sensor.elecq_au101_power`
- `sensor.elecq_au101_power_smoothed`
- `sensor.elecq_au101_energy`
- `sensor.elecq_au101_session_energy`

### Binary Sensors
- `binary_sensor.elecq_au101_plugged_in`
- `binary_sensor.elecq_au101_charger_charging`

### Switches
- `switch.elecq_au101_charger_remote_charging`

---

# 🖥 Example Lovelace Card

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Elecq AU101
    entities:
      - entity: sensor.elecq_au101_status
        name: Status
      - entity: sensor.elecq_au101_charging_state
        name: Charging State

  - type: grid
    square: false
    columns: 3
    cards:
      - type: entity
        entity: binary_sensor.elecq_au101_plugged_in
      - type: entity
        entity: binary_sensor.elecq_au101_charger_charging
      - type: entity
        entity: switch.elecq_au101_charger_remote_charging

  - type: grid
    square: false
    columns: 2
    cards:
      - type: entity
        entity: sensor.elecq_au101_session_energy
      - type: entity
        entity: sensor.elecq_au101_power
```

---

# 🛠 Development

```bash
git clone https://github.com/BashTheDog/elecq-ocpp-ha
```

Pull requests welcome.

---

# 🏷 Versioning

- Semantic Versioning  
- Version in `manifest.json` must match GitHub release tag  
- Releases should follow `vX.Y.Z`

---

# 📄 License

MIT License © 2025 **BashTheDog**
