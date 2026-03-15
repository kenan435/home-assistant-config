#!/bin/sh
set -e
# Options (ha_url, ha_token) are read from /data/options.json by runner.py
ADDON_DIR="$(dirname "$0")"
exec python3 "$ADDON_DIR/runner.py"
