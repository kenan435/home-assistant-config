#!/usr/bin/env python3
"""
Loxone Intercom UDP doorbell listener.

Listens on UDP port 8112 for Loxone intercom **UDP broadcast** packets. When
command ID '50' (doorbell pressed) is received, triggers the Home Assistant
doorbell automation via REST API.

Payload format (Loxone intercom; indices are 0-based):
  Bytes 00-01 : Message counter (hex as two ASCII chars). Per button press,
                command 50 is sent **twice**; the counter in the second packet
                is always +1 vs. the first.
  Byte  02    : Fixed '@' (ASCII 0x40)  — not 0x23 (some PDFs swap @/# wrongly)
  Bytes 03-04 : Command ID (two ASCII hex chars)
  Byte  05    : Fixed '#' (ASCII 0x23)  — not 0x40
  Bytes 06-24 : Payload data (ASCII), when present
  Bytes 25-26 : Checksum over payload (when present)

Known command IDs:
  '0A' : Firmware version text
  '14' : Unknown
  '4C' : After each button press + heartbeat every ~10 s
  '50' : Doorbell button pressed (two packets per press)

Intercom is often at 192.168.136.98, camera at 192.168.136.99 (verify on your LAN).

Run on the same network as the intercom (e.g. HA host or Raspberry Pi).
Requires: HA URL and long-lived access token (env or .env file).

  export HA_URL=http://homeassistant.local:8123
  export HA_TOKEN=your_long_lived_token
  python3 loxone_doorbell_udp.py

Or run as a systemd service (see README in scripts/).

Test locally: send to 127.0.0.1 (same machine as the script), not to the HA host:
  echo -n $'\x30\x31\x40\x35\x30\x23' | nc -u -w1 127.0.0.1 8112
("01@50#" = counter 01, command 50 = doorbell)
"""

import os
import socket
import sys
import time
import urllib.request
import urllib.error

UDP_PORT = 8112
# Command ID '50' = doorbell button pressed (two messages per press)
CMD_DOORBELL = b"50"
# Minimum: counter(2) + '@'(1) + cmd(2) + '#'(1)
MIN_LEN = 6
# Loxone sends two UDP packets per ring; debounce so HA runs once per press.
DEBOUNCE_SECONDS = 1.5
_last_ha_trigger_monotonic: float = 0.0

HA_URL = os.environ.get("HA_URL", "http://homeassistant.local:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
AUTOMATION_ENTITY = "automation.front_door_motion_push_notification"


def trigger_doorbell():
    global _last_ha_trigger_monotonic
    if not HA_TOKEN:
        print("HA_TOKEN not set, skipping trigger", file=sys.stderr)
        return
    now = time.monotonic()
    if now - _last_ha_trigger_monotonic < DEBOUNCE_SECONDS:
        print("Debounce: skipped duplicate doorbell packet (same press)", file=sys.stderr)
        return
    _last_ha_trigger_monotonic = now
    url = f"{HA_URL}/api/services/automation/trigger"
    entity_id = AUTOMATION_ENTITY.decode() if isinstance(AUTOMATION_ENTITY, bytes) else str(AUTOMATION_ENTITY)
    data = f'{{"entity_id": "{entity_id}"}}'.encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {HA_TOKEN.decode() if isinstance(HA_TOKEN, bytes) else HA_TOKEN}",
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
    # Byte 2 = '@' (0x40), bytes 3-4 = "50", byte 5 = '#' (0x23)
    if data[2] != 0x40:
        return False
    if data[3:5] != CMD_DOORBELL:
        return False
    if data[5] != 0x23:
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
        else:
            # Debug: log non-doorbell UDP so you see traffic (e.g. when testing with nc)
            if len(data) >= 1:
                print(f"[debug] UDP from {addr} len={len(data)} raw={data[:20]!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
