# Loxone intercom doorbell → Home Assistant

The Loxone intercom sends UDP broadcast packets on **port 8112** when the doorbell is pressed (command ID `50`). The script `loxone_doorbell_udp.py` listens for those packets and triggers your existing HA doorbell automation (push notification).

**Deployment:** The script runs **outside** Home Assistant (on a host that can bind to UDP 8112). HA’s Terminal & SSH app can only expose one port (SSH), so run the script on your Mac, a Raspberry Pi, or another always-on device on the same network. It then calls the HA API to trigger the doorbell automation.

## Requirements

- Python 3 (no extra packages)
- Script must run on a host on the same network as the intercom (e.g. the same machine as Home Assistant, or another always-on device)
- Home Assistant long-lived access token

## 1. Create a long-lived access token

In Home Assistant: **Profile** (bottom left) → **Security** → **Long-Lived Access Tokens** → **Create token**. Name it e.g. "Loxone doorbell" and copy the token.

## 2. Run the script

```bash
cd scripts
export HA_URL="http://homeassistant.local:8123"   # or http://192.168.x.x:8123
export HA_TOKEN="your_long_lived_token_here"
python3 loxone_doorbell_udp.py
```

Intercom IPs from your docs: **192.168.136.98** (intercom), **192.168.136.99** (camera). The script listens on `0.0.0.0:8112` so it receives broadcasts from any source.

## 3. Run as a service (e.g. on Raspberry Pi)

Create `/etc/systemd/system/loxone-doorbell.service`:

```ini
[Unit]
Description=Loxone doorbell UDP listener for Home Assistant
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/path/to/HomeAssistent/scripts
Environment=HA_URL=http://homeassistant.local:8123
Environment=HA_TOKEN=your_token_here
ExecStart=/usr/bin/python3 loxone_doorbell_udp.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable loxone-doorbell
sudo systemctl start loxone-doorbell
sudo systemctl status loxone-doorbell
```

Keep `HA_TOKEN` secure (e.g. use a file with `EnvironmentFile=/etc/loxone-doorbell.env` and `chmod 600`).

## 4. Run on Mac (background / at login)

To run the listener on your Mac so it starts when you’re on the same network:

```bash
# One-off: run in background (stops when Mac sleeps or you kill it)
cd /path/to/HomeAssistent/scripts
nohup env HA_URL="http://192.168.136.136:8123" HA_TOKEN="your_token" python3 loxone_doorbell_udp.py >> ~/doorbell.log 2>&1 &
```

**LaunchAgent (start at login):** Create `~/Library/LaunchAgents/com.home.loxone-doorbell.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.home.loxone-doorbell</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/kenan.karamehmedovic/Developer/github.com/HomeAssistent/scripts/loxone_doorbell_udp.py</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HA_URL</key>
    <string>http://192.168.136.136:8123</string>
    <key>HA_TOKEN</key>
    <string>YOUR_LONG_LIVED_TOKEN</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/loxone-doorbell.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/loxone-doorbell.err</string>
</dict>
</plist>
```

Then: `launchctl load ~/Library/LaunchAgents/com.home.loxone-doorbell.plist`  
Replace the path and token with your values. Regenerate the token if the plist is on a shared machine.

## What gets triggered

The script calls the same automation as your KNX doorbell: **Front Door Motion - Push Notification** (`automation.front_door_motion_push_notification`). So you get the same push to your phone whether the trigger is KNX or the Loxone UDP packet.
