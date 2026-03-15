#!/usr/bin/env python3
"""Load add-on options from /data/options.json and run the doorbell script."""
import json
import os
import sys

OPTIONS_FILE = "/data/options.json"
SCRIPT = "/config/scripts/loxone_doorbell_udp.py"

def main():
    try:
        with open(OPTIONS_FILE) as f:
            opts = json.load(f)
        os.environ["HA_URL"] = opts.get("ha_url", "") or os.environ.get("HA_URL", "http://homeassistant.local:8123")
        os.environ["HA_TOKEN"] = opts.get("ha_token", "") or os.environ.get("HA_TOKEN", "")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Warning: could not read {OPTIONS_FILE}: {e}", file=sys.stderr)

    if not os.path.isfile(SCRIPT):
        print(f"Error: {SCRIPT} not found. Ensure this repo is in /config (e.g. clone or copy scripts/).", file=sys.stderr)
        sys.exit(1)

    os.execv(SCRIPT, [SCRIPT])

if __name__ == "__main__":
    main()
