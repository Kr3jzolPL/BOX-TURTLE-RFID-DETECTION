# main.py - TCA9548A (8ch) + 4x PN532 on channels 0..3
from machine import I2C, Pin
import time
from pn532_i2c import PN532

TCA_ADDR = 0x70
LANE_CHANNELS = {
    1: 3,
    2: 2,
    3: 1,
    4: 0,
}

# Auto "re-arm" when tag disappears for this long
REMOVE_TIMEOUT_MS = 1500

# Pico I2C0 pins (change if needed)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=200_000)

pn = PN532(i2c, timeout_ms=2000)

def mux_select(ch: int):
    # Select one channel (0..7)
    i2c.writeto(TCA_ADDR, bytes([1 << ch]))
    time.sleep_ms(1)

def uid_hex(b):
    return "".join("{:02X}".format(x) for x in b)

# Per-lane state
last_uid = {lane: None for lane in LANE_CHANNELS}
last_seen = {lane: 0 for lane in LANE_CHANNELS}

print("INIT...")

# Initialize each PN532 channel
for lane, ch in LANE_CHANNELS.items():
    mux_select(ch)
    try:
        pn.sam_config()
        # Optional: firmware check (comment out if you don't care)
        # fw = pn.firmware()
        print("READY LANE={} CH={}".format(lane, ch))
    except Exception as e:
        print("INIT_ERR LANE={} CH={} {}".format(lane, ch, e))

print("RUNNING")

while True:
    now = time.ticks_ms()

    for lane, ch in LANE_CHANNELS.items():
        mux_select(ch)

        try:
            uid = pn.scan_uid()
        except Exception as e:
            # Don't spam too hard
            # print("ERR LANE={} {}".format(lane, e))
            uid = None

        if uid:
            last_seen[lane] = now
            # Print only once per insertion / UID change
            if last_uid[lane] != uid:
                last_uid[lane] = uid
                print("LANE={} UID={}".format(lane, uid_hex(uid)))
        else:
            # If we haven't seen a tag for a while, re-arm (allow next detection)
            if last_uid[lane] is not None:
                if time.ticks_diff(now, last_seen[lane]) > REMOVE_TIMEOUT_MS:
                    last_uid[lane] = None

    time.sleep_ms(40)
