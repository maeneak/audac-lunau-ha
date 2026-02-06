# Audac Luna-U (HACS Integration)

Home Assistant integration for the Audac Luna-U audio matrix. It exposes zone control (volume, mute, source/route) as `media_player` entities and GPIO outputs as `switch` entities.

**Highlights**
- Config flow setup (UI)
- Default 8 zones, 8 inputs
- Zone `media_player` control: volume, mute, source select
- GPIO output switches with custom names

**Requirements**
- Audac Luna-U reachable over TCP/IP
- Luna-U ASCII control enabled and network accessible

**Protocol Notes**
The Luna-U uses an ASCII command protocol over TCP. This integration connects via TCP port `5001` by default and sends ASCII commands framed with `#|...|` and `CRLF` line endings. CRC is not used (`U`).

**Installation (HACS)**
1. In HACS, add a custom repository:
   - Repository: `https://github.com/maeneak/audac-lunau-ha`
   - Category: Integration
2. Install **Audac Luna-U**.
3. Restart Home Assistant.
4. Add the integration via **Settings → Devices & Services → Add Integration**.

**Configuration**
This integration is configured via the UI (Config Flow). There is no `configuration.yaml` setup.

During setup, you will provide:
- Host
- Port (default `5001`)
- Device address (default `1`)

**Options**
After adding the integration, go to the integration’s **Options** to configure:
- Zones (default `8`)
- Inputs (default `8`)
- GPIO outputs (default `12`)
- Poll interval in seconds (default `10`)
- Zone names (comma-separated)
- Input names (comma-separated)
- GPIO names (comma-separated)

Example names (comma-separated):
```
Zone 1, Zone 2, Lobby, Patio, Office, Bar, Dining, Lounge
Input 1, Input 2, TV, Music, Mic 1, Mic 2, PC, Aux
Door, Projector, Screen, Amp, Relay 5, Relay 6, Relay 7, Relay 8, Relay 9, Relay 10, Relay 11, Relay 12
```

**Entities**
- `media_player` (one per zone)
  - Volume (mapped from -90dB..0dB to 0.0..1.0)
  - Mute
  - Source select (routing)
- `switch` (one per GPIO output)
  - On/Off maps to `GPO_ENABLE`

**Source/Route Mapping**
The Luna-U routing command accepts:
- `0` = Off
- `1..N` = Input index

The integration exposes sources as `Off` + your input list.

**GPIO Outputs**
GPIO outputs are exposed as switches. Turning a switch on/off triggers:
- `SET_REQ^GPO>n>GPO_TRIGGER>1^GPO_ENABLE|TRUE|FALSE`

**Known Limitations**
- The manual does not provide name discovery. Zone/Input/GPIO names must be configured manually.
- State is polled (no push updates).
- Mixer controls are not exposed (routing only).

**Troubleshooting**
- Verify the Luna-U is reachable on TCP port `5001`.
- Ensure the device address matches the Luna-U configuration.
- If entities show `unknown`, increase the poll interval or confirm the Luna-U responds to `GET_REQ`.

**Contributing**
PRs welcome. If you have protocol examples or a simulator, please share them to improve parsing and reliability.
