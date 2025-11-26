\# Elecq OCPP 2.0.1 Home Assistant Integration



This custom integration allows Home Assistant to act as an OCPP 2.0.1 server

for the Elecq AU101 charger.



\## Features

\- Full OCPP 2.0.1 WebSocket server inside Home Assistant

\- Remote start/stop (RequestStartTransaction / RequestStopTransaction)

\- Power, energy, session metrics

\- Plugged-in and charging detection

\- Charging state (from TransactionEvent)

\- Auto disconnect when EV unplugged (stoppedReason = EVDisconnected)



\## Installation (HACS)

1\. Go to HACS → Integrations

2\. Click \*\*⋮\*\* (top right) → \*\*Custom repositories\*\*

3\. Add:  

&nbsp;  `https://github.com/<YOUR\_USERNAME>/elecq-ocpp-ha`

4\. Category: \*\*Integration\*\*

5\. Install “Elecq OCPP 2.0.1”

6\. Restart Home Assistant



\## Configuration

After restart:



1\. Go to \*\*Settings → Devices \& Integrations\*\*

2\. Click \*\*Add Integration\*\*

3\. Search for \*\*Elecq OCPP\*\*

4\. Enter:

&nbsp;  - WebSocket port (e.g., 9006)

&nbsp;  - EVSE ID (usually 1)

&nbsp;  - Connector ID (usually 1)

&nbsp;  - ID Token



\## Point the charger to HA

In the Elecq app or charger config, set:

ws://HOME\_ASSISTANT\_IP:9006/AU101-serial



Protocol: \*\*ocpp2.0.1\*\*



\## License

MIT



