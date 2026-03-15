# Loxone Doorbell (HA Add-on)

Runs the Loxone intercom doorbell listener as a background service on your Home Assistant host. Listens on UDP port 8112 for command `50` (doorbell pressed) and triggers the doorbell automation.

## Install from this repo

1. In Home Assistant: **Settings** → **Apps** → **App store** (three dots) → **Repositories**.
2. Add: `https://github.com/kenan435/home-assistant-config`
3. Refresh; under **App store** you should see **Loxone Doorbell**. Install it.
4. **Configuration** tab: set **HA URL** (e.g. `http://homeassistant.local:8123`) and **HA token** (long-lived token from Profile → Security).
5. Ensure `/config/scripts/loxone_doorbell_udp.py` exists (this repo’s `scripts/` folder must be in your HA config, e.g. via Git pull).
6. **Start** the add-on and enable **Start on boot** if you want.

## Requirements

- Your HA config must contain `scripts/loxone_doorbell_udp.py` (clone or copy this repo into `/config`).
- Port **8112/UDP** is used by the add-on; nothing else should bind it.
