# Elecq AU101 OCPP – Home Assistant Custom Integration

<p>
  <img src="https://raw.githubusercontent.com/BashTheDog/elecq-ocpp-ha/main/assets/elecq_badge_square.png" width="160" alt="Elecq Logo">
</p>

[![GitHub Release](https://img.shields.io/github/v/release/BashTheDog/elecq-ocpp-ha?style=for-the-badge)](https://github.com/BashTheDog/elecq-ocpp-ha/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue.svg?style=for-the-badge)](https://hacs.xyz/)
[![GitHub Stars](https://img.shields.io/github/stars/BashTheDog/elecq-ocpp-ha?style=for-the-badge)](https://github.com/BashTheDog/elecq-ocpp-ha/stargazers)

---

# ⚡ Elecq AU101 OCPP Integration

A Home Assistant integration for the **Elecq AU101** EV Charger using an embedded **OCPP 2.0.1 WebSocket server**.

This integration provides:

- Real-time **charger status**
- EV **plugged-in** detection
- Detailed **charging state** (`Charging`, `SuspendedEV`, `Idle`, etc.)
- **Start/Stop charging** with true OCPP commands
- Accurate power and energy tracking
- Greyed-out switch while waiting for charger responses
- No cloud required — fully local

---

# 🖼 Integration Logo (Smaller)

<p>
  <img src="https://raw.githubusercontent.com/BashTheDog/elecq-ocpp-ha/main/assets/elecq_badge_square.png" width="160" alt="Elecq Logo">
</p>

---

# 🚀 Features

### 🟢 Charger Status
- Available / Occupied / Faulted / Unavailable

### 🔌 EV Plug Detection
- Instant plug/unplug recognition  
- Uses `stoppedReason: EVDisconnected` for accuracy

### 🔋 Charging State
- Real Charging
- EVConnected
- SuspendedEV → **Possibly fully charged**
- Idle / Finished

### ⚡ Energy Metrics
- Real-time Power (kW)
- Smoothed Power
- Total Energy (kWh)
- Session Energy

### 🆘 Smart Charging Switch
- Reflects *actual* charger state  
- Grey-out while awaiting OCPP response  
- Safe rejection when EV is full or unplugged  

---

# 📦 Installation

## Option A — HACS (Custom Repository)

1. Open **HACS → Integrations**
2. Add custom repository:

```
https://github.com/BashTheDog/elecq-ocpp-ha
```

3. Select category: **Integration**
4. Install & restart Home Assistant

---

## Option B — Manual Installation

Copy:

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

Open **Settings → Devices & Services → Add Integration → Elecq OCPP**

| Field | Meaning |
|-------|---------|
| Port | WebSocket port (default `9006`) |
| ID Token | Used in RequestStartTransaction |
| EVSE ID | Typically `1` |
| Connector ID | Typically `1` |

---

# 🔗 Elecq Charger OCPP Setup

In the Elecq mobile app, set:

```
ws://<home-assistant-ip>:9006/AU101B2G00127D
```

OCPP Version: **2.0.1**

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

### Switch
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
      - entity: sensor.elecq_au101_charging_state

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

---

# 🏷 Versioning

- Follows Semantic Versioning  
- Version must match `manifest.json`  
- Releases should follow `vX.Y.Z`

---

# 📄 License

MIT License © 2025 **BashTheDog**
