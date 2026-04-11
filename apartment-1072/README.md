# Home Assistant — Apartment 1072

KNX-based Home Assistant config for apartment 1072 (Isaria WA10c).  
All group addresses sourced from ETS5 project file `01.10.2025_Isaria_WA10c.knxproj`.

## Setup

1. Flash **Home Assistant OS** to a Pi SD card.
2. Boot the Pi, complete onboarding at `http://<PI_IP>:8123`.
3. Install **Terminal & SSH** and **File editor** add-ons.
4. SSH in or use the web terminal:
   ```bash
   cd /config
   git clone https://github.com/kenan435/home-assistant-config-1072.git .
   ```
5. Create `/config/secrets.yaml` (not in git):
   ```yaml
   knx_gateway_host: 192.168.x.x  # IP of KNX IP interface on apartment network
   ```
6. Find the KNX gateway IP on the apartment network:
   ```bash
   nmap -p 3671 192.168.x.0/24
   ```
7. Restart Home Assistant.

## KNX Group Address Ranges

| Range | Function |
|---|---|
| `11/4/10–11` | Doorbell |
| `11/4/12–39` | Lights & switches |
| `11/4/40–54` | Sockets |
| `11/4/70–119` | Heating (5 zones) |
| `11/4/170–224` | Blinds (8 covers) |
| `11/5/x` | Button panels (read-only reference) |

## Rooms

| Room | Heating zone |
|---|---|
| Living / Dining / Kitchen | Combined zone (`11/4/70`) |
| Bedroom | `11/4/103` |
| Kids Room | `11/4/92` |
| Bathroom | `11/4/114` |
| WC | `11/4/81` |
