# Loxone Doorbell (HA Add-on)

Runs the Loxone intercom doorbell listener as a background service on your Home Assistant host. Listens on UDP port 8112 for command `50` (doorbell pressed) and triggers the doorbell automation.

## Install from this repo

1. In Home Assistant: **Settings** → **Apps** → **App store** (three dots) → **Repositories**.
2. Add: `https://github.com/kenan435/home-assistant-config`
3. Refresh; under **App store** you should see **Loxone Doorbell**. Install it.
4. **Configuration** tab: set **HA URL** and **HA token** (long-lived token from Profile → Security).  
   On the **same Pi** as HA, use **`http://127.0.0.1:8123`** (avoids mDNS issues).
5. Ensure `/config/scripts/loxone_doorbell_udp.py` exists (this repo’s `scripts/` folder must be in your HA config, e.g. via Git pull).
6. **Start** the add-on and enable **Start on boot** if you want.
7. After updating add-on files from git, **restart** the add-on (or reinstall from store if HA doesn’t pick up `config.yaml` changes).

## Requirements

- Your HA config must contain `scripts/loxone_doorbell_udp.py` (clone or copy this repo into `/config`).
- Port **8112/UDP** on the **host** (add-on uses **host network** so Loxone **broadcast** UDP is received).

## Troubleshooting: you ring but the add-on log stays empty

1. Use an add-on build with **`host_network: true`** (see `config.yaml` in this repo). Plain Docker **port publish** often **does not** deliver **broadcast** UDP to the container.
2. Pi and Loxone must be on the **same subnet** (e.g. both `192.168.136.x`). Guest WiFi / another VLAN usually blocks broadcasts.
3. From a PC on the LAN:  
   `echo -n $'\x30\x31\x40\x35\x30\x23' | nc -u -w1 <PI_LAN_IP> 8112`  
   You should see `Doorbell packet` in the add-on log if UDP reaches the Pi.
