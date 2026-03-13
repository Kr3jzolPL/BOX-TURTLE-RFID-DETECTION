#!/usr/bin/env python3
import re
import time
from typing import Any, Dict, Optional

import requests
import serial

# ---------------- CONFIG ----------------
PICO_PORT = "/dev/pico-nfc"
BAUD = 115200

SPOOLMAN = "http://192.168.1.39:7912"
MOONRAKER = "http://127.0.0.1:7125"

REFRESH_SECONDS = 30
ALLOW_ARCHIVED = True
COOLDOWN_SECONDS = 1.0
# ----------------------------------------

LINE_RE = re.compile(r"LANE=(\d+)\s+UID=([0-9A-F]+)", re.I)

# -------- Printer State Cache --------
_last_state_check = 0
_cached_printing = False


def printer_is_printing() -> bool:
    global _last_state_check, _cached_printing
    now = time.time()

    # Only check once per second
    if now - _last_state_check > 1:
        try:
            r = requests.get(
                f"{MOONRAKER}/printer/objects/query?print_stats",
                timeout=0.5,
            )
            state = r.json()["result"]["status"]["print_stats"]["state"]
            _cached_printing = (state == "printing")
        except Exception:
            _cached_printing = False

        _last_state_check = now

    return _cached_printing


def lane_name(lane_num: int) -> str:
    return f"lane{lane_num}"


def moonraker_run_gcode(script: str) -> None:
    r = requests.post(
        f"{MOONRAKER}/printer/gcode/script",
        json={"script": script},
        timeout=3,
    )
    r.raise_for_status()


def _normalize_external_id(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()

    while (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()

    s = s.upper()
    return s if s else None


def extract_external_id(spool: Dict[str, Any]) -> Optional[str]:
    extra = spool.get("extra")
    if isinstance(extra, dict):
        ext = _normalize_external_id(extra.get("external_id"))
        if ext:
            return ext

    extra_fields = spool.get("extra_fields")
    if isinstance(extra_fields, dict):
        ext = _normalize_external_id(extra_fields.get("external_id"))
        if ext:
            return ext

    if isinstance(extra_fields, list):
        for item in extra_fields:
            if not isinstance(item, dict):
                continue
            name = (item.get("name") or item.get("key") or "").strip().lower()
            if name == "external_id":
                ext = _normalize_external_id(item.get("value"))
                if ext:
                    return ext

    if "external_id" in spool:
        ext = _normalize_external_id(spool.get("external_id"))
        if ext:
            return ext

    return None


def fetch_spool_map() -> Dict[str, int]:
    params = {"limit": 10000}
    if ALLOW_ARCHIVED:
        params["allow_archived"] = "true"

    r = requests.get(f"{SPOOLMAN}/api/v1/spool", params=params, timeout=5)
    r.raise_for_status()
    spools = r.json()

    m: Dict[str, int] = {}
    for s in spools:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        if sid is None:
            continue
        ext = extract_external_id(s)
        if not ext:
            continue
        if ext not in m:
            m[ext] = int(sid)
    return m


def main() -> None:
    ser = serial.Serial(PICO_PORT, BAUD, timeout=1)

    spool_map: Dict[str, int] = {}
    last_refresh = 0.0
    last_seen: Dict[int, tuple[str, float]] = {}

    while True:
        now = time.time()

        # Refresh spool map periodically
        if (now - last_refresh) > REFRESH_SECONDS or not spool_map:
            try:
                spool_map = fetch_spool_map()
                last_refresh = now
            except Exception as e:
                try:
                    moonraker_run_gcode(
                        f'ReSPOND PREFIX="NFC" MSG="Spoolman refresh error: {e}"'
                    )
                except Exception:
                    pass
                time.sleep(2)

        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        m = LINE_RE.search(line)
        if not m:
            continue

        # 🔒 Ignore RFID silently during active print
        if printer_is_printing():
            continue

        lane_num = int(m.group(1))
        uid_hex = m.group(2).strip().upper()
        lname = lane_name(lane_num)

        prev = last_seen.get(lane_num)
        if prev and prev[0] == uid_hex and (now - prev[1]) < COOLDOWN_SECONDS:
            continue
        last_seen[lane_num] = (uid_hex, now)

        spool_id = spool_map.get(uid_hex)

        if spool_id is None:
            try:
                spool_map = fetch_spool_map()
                last_refresh = time.time()
                spool_id = spool_map.get(uid_hex)
            except Exception:
                spool_id = None

        if spool_id is None:
            moonraker_run_gcode(
                f'ReSPOND PREFIX="NFC" MSG="No spool found with external_id={uid_hex} (lane={lname})"'
            )
            continue

        moonraker_run_gcode(f"SET_SPOOL_ID LANE={lname} SPOOL_ID={spool_id}")
        moonraker_run_gcode(
            f'ReSPOND PREFIX="NFC" MSG="Set {lname} -> SPOOL_ID {spool_id} (external_id={uid_hex})"'
        )


if __name__ == "__main__":
    main()
