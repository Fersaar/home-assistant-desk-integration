# Desk Integration for Home Assistant

A custom [Home Assistant](https://www.home-assistant.io/) integration that connects to a DIY motorized sit/stand desk over a local HTTP API.

## Features

- **Cover** — raise, lower, stop, and set a target position (0–100 %)
- **Height number** — move to an exact height in mm via a slider
- **Sensors** — current position and movement state (moving up / moving down / not moving)
- **Limit numbers** — configure upper and lower movement bounds
- **Auto-calibrate button** — trigger the firmware's calibration routine

Communication is entirely local (no cloud) via the desk's built-in web server.

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant.
2. Add this repository as a **custom repository** (type: Integration).
3. Search for "Fersaar Desk Integration" and install.
4. Restart Home Assistant.

### Manual

Copy the `custom_components/desk_integration` folder into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

After installation, go to **Settings → Devices & Services → Add Integration** and search for **Desk**. Enter the IP address or hostname of the desk's web interface.

## Requirements

- Home Assistant 2026.3.2 or later
- The desk firmware must expose the HTTP API described in `openapi.yaml`

## Development

```bash
scripts/setup    # install dependencies
scripts/develop  # start HA with the integration loaded
scripts/lint     # run linters
```

## License

See [LICENSE](LICENSE) for details.
