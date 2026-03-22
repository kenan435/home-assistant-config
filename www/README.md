# Doorbell chime for Sonos

1. Add an MP3 (or other format your Sonos supports) as **`doorbell.mp3`** on your Home Assistant host at **`/config/www/doorbell.mp3`**.
2. It is served at **`http://<your-ha-ip>:8123/local/doorbell.mp3`** (not HTTPS unless you terminate TLS in front of HA).
3. In **Settings → Devices & services → Helpers → Doorbell chime URL**, set the full URL. Sonos often **cannot resolve** `homeassistant.local`; use your Home Assistant **LAN IP** (e.g. `http://192.168.1.50:8123/local/doorbell.mp3`).
4. Reload automations (or restart HA) after changing helpers, if needed.

The doorbell automation plays this URL on **`media_player.living_room`** and **`media_player.kitchen`** with **`announce: true`** so music is ducked briefly.

Optional: instead of a local file, set the helper to any **HTTP(S) URL** your Sonos can reach (short MP3).
