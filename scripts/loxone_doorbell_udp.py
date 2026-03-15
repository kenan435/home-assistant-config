#!/usr/bin/env python3
"""
Loxone Intercom UDP doorbell listener.

Listens on UDP port 8112 for Loxone intercom packets. When command ID '50'
(doorbell button pressed) is received, triggers the Home Assistant doorbell
automation via REST API.

Payload format (from Loxone docs):
  Bytes 0-1 : Message counter (hex, 2 ASCII chars)
  Byte  2   : Fixed '@' (0x40)
  Bytes 3-4 : Command ID (hex, 2 ASCII chars) — '50' = doorbell pressed
  Byte  5   : Fixed '#' (0x23)
  ...

Run on the same network as the intercom (e.g. HA host or Raspberry Pi).
Requires: HA URL and long-lived access token (env or .env file).

  export HA_URL=http://homeassistant.local:8123
  export HA_TOKEN=your_long_lived_token
  python3 loxone_doorbell_udp.py

Or run as a systemd service (see README in scripts/).
"""

import os
import socket
import sys
import urllib.request
import urllib.error

UDP_PORT = 8112
# Command ID '50' = doorbell button pressed (two messages per press)
CMD_DOORBELL = b"50"
# Byte 2 must be '@' (0x40), we check bytes 3-4 for "50"
MIN_LEN = 6

HA_URL = os.environ.get("HA_URL", "http://homeassistant.local:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
AUTOMATION_ENTITY = "automation.front_door_motion_push_notification"


def trigger_doorbell():
    if not HA_TOKEN:
        print("HA_TOKEN not set, skipping trigger", file=sys.stderr)
        return
    url = f"{HA_URL}/api/services/automation/trigger"
    data = '{"entity_id": "' + AUTOMATION_ENTITY + '"}' .encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                print("Doorbell triggered in HA")
            else:
                print(f"HA returned status {r.status}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        print(f"HA API error: {e.code} {e.reason}", file=sys.stderr)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)


def is_doorbell_packet(data: bytes) -> bool:
    if len(data) < MIN_LEN:
        return False
    # Byte 2 = '@' (0x40), bytes 3-4 = "50"
    if data[2] != 0x40:
        return False
    if data[3:5] != CMD_DOORBELL:
        return False
    return True


def main():
    if not HA_TOKEN:
        print("Warning: HA_TOKEN not set. Doorbell events will be logged but HA will not be triggered.", file=sys.stderr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", UDP_PORT))
    except OSError as e:
        print(f"Bind failed: {e}. Port {UDP_PORT} in use or permission denied?", file=sys.stderr)
        sys.exit(1)
    print(f"Listening for Loxone doorbell UDP on port {UDP_PORT} ...")
    while True:
        data, addr = sock.recvfrom(1024)
        if is_doorbell_packet(data):
            print(f"Doorbell packet from {addr}")
            trigger_doorbell()


if __name__ == "__main__":
    main()
