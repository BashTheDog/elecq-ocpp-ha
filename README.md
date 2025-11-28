# Elecq AU101 OCPP – Home Assistant Custom Integration

![Elecq OCPP Badge](https://raw.githubusercontent.com/BashTheDog/elecq_ocpp/main/assets/elecq_badge_square.png)

[![GitHub Release](https://img.shields.io/github/v/release/BashTheDog/elecq_ocpp?style=for-the-badge)](https://github.com/BashTheDog/elecq_ocpp/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue.svg?style=for-the-badge)](https://hacs.xyz/)
[![GitHub Stars](https://img.shields.io/github/stars/BashTheDog/elecq_ocpp?style=for-the-badge)](https://github.com/BashTheDog/elecq_ocpp/stargazers)

---

# ⚡ Elecq AU101 OCPP Integration

A modern Home Assistant integration for the **Elecq AU101** EV Charger using an **embedded OCPP 2.0.1 WebSocket server** written in Python.

This integration communicates directly with the charger, providing:

- Real-time **status**, **charging state**, and **energy metrics**
- EV **plugged-in** detection
- Fully local **start/stop charging control** using OCPP
- Smooth, reliable charger state representation in Home Assistant
- Accurate handling of full battery condition (`SuspendedEV`)  
- Friendly & compact Lovelace card example

---

# 🖼 Integration Logo

![Integration Logo](https://raw.githubusercontent.com/BashTheDog/elecq_ocpp/main/assets/elecq_badge_square.png)

---

# 🚀 Features

### 🟢 Real-time Charger State
- Available  
- Occupied  
- Faulted  
- Unavailable  

### 🔌 EV Plug Detection
- Detects when your EV is connected/disconnected
- Uses `EVDisconnected` stop events correctly

### 🔋 Charging State (OCPP)
- Charging  
- EVConnected  
- SuspendedEV → **“Suspended by EV (possibly full)”**  
- Idle / Finished  

### ⚡ Energy & Power Monitoring
- Instantaneous power (kW)
- Smoothed 5-sample average power
- Total imported energy (kWh)
- Per-session energy

### 🆘 Smart Remote Charging Switch
- Switch reflects **actual** charger state (not optimistic)  
- Greyed-out while waiting for charger response  
- Rejects invalid start/stop calls safely

---

# 📦 Installation

## **HACS (Custom Repository)**

1. Open **HACS → Integrations**
2. Add custom repository:
   ```
   https://github.com/BashTheDog/elecq_ocpp
   ```
3. Category: **Integration**
4. Install & restart Home Assistant

## **Manual Install**

Copy `custom_components/elecq_ocpp` into:

```
<config>/custom_components/elecq_ocpp/
```

Restart Home Assistant.

---

# 🔧 Configuration

Go to **Settings → Devices & Services → Add Integration → Elecq OCPP**

| Field | Description |
|-------|-------------|
| **Port** | WebSocket port (default `9006`) |
| **ID Token** | Token for transaction start (`ElecqAutoStart`) |
| **EVSE ID** | Usually `1` |
| **Connector ID** | Usually `1` |

---

# 🔗 Configure Your Elecq AU101

Set OCPP server in the Elecq app:

```
ws://<home_assistant_ip>:9006/AU101B2G00127D
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
- `switch.elecq_au101_remote_charging`

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
        entity: switch.elecq_au101_remote_charging

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
git clone https://github.com/BashTheDog/elecq_ocpp
```

Pull requests welcome!

---

# 🏷 Versioning

- Semantic Versioning (`1.0.0`, `1.1.0`, etc.)
- Version must match `manifest.json`
- GitHub releases should follow `v1.x.x`

---

# 📄 License

MIT License © 2025 **BashTheDog**
