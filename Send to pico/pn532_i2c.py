# pn532_i2c.py (MicroPython) - robust PN532 I2C framing WITHOUT relying on status byte
import time

PN532_ADDR = 0x24

HOSTTOPN532 = 0xD4
PN532TOHOST = 0xD5

CMD_GET_FIRMWARE_VERSION = 0x02
CMD_SAMCONFIGURATION     = 0x14
CMD_INLISTPASSIVETARGET  = 0x4A

ACK_FRAME = b"\x00\x00\xFF\x00\xFF\x00"

def _checksum8(data):
    return (-sum(data)) & 0xFF

class PN532:
    def __init__(self, i2c, addr=PN532_ADDR, timeout_ms=1200):
        self.i2c = i2c
        self.addr = addr
        self.timeout_ms = timeout_ms
        # wake kick (helps some boards)
        try:
            self.i2c.writeto(self.addr, b"\x00")
        except OSError:
            pass
        time.sleep_ms(50)

    def _write(self, b):
        self.i2c.writeto(self.addr, b"\x00" + b)

    def _read_buf(self, n=64):
        return self.i2c.readfrom(self.addr, n)

    def _frame(self, payload):
        ln  = len(payload) & 0xFF
        lcs = (-ln) & 0xFF
        dcs = _checksum8(payload)
        return bytes([0x00, 0x00, 0xFF, ln, lcs]) + payload + bytes([dcs, 0x00])

    def _parse_any_frame(self, raw):
        # raw may include status byte at [0]; try both offsets
        for start in (0, 1):
            buf = raw[start:]
            idx = buf.find(b"\x00\x00\xFF")
            if idx < 0:
                continue
            buf = buf[idx:]

            if buf.startswith(ACK_FRAME):
                return ("ACK", None)

            if len(buf) < 8:
                continue

            ln  = buf[3]
            lcs = buf[4]
            if ((ln + lcs) & 0xFF) != 0:
                continue

            data_start = 5
            data_end   = data_start + ln
            if data_end + 1 > len(buf):
                continue

            data = buf[data_start:data_end]
            dcs  = buf[data_end]
            if (_checksum8(data) & 0xFF) != dcs:
                continue

            return ("DATA", data)

        return None

    def _read_frame(self):
        deadline = time.ticks_add(time.ticks_ms(), self.timeout_ms)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            try:
                raw = self._read_buf(64)
            except OSError:
                time.sleep_ms(10)
                continue

            parsed = self._parse_any_frame(raw)
            if parsed:
                return parsed

            time.sleep_ms(10)

        raise OSError("PN532 timeout waiting frame")

    def _command(self, cmd, params=b""):
        payload = bytes([HOSTTOPN532, cmd]) + params
        self._write(self._frame(payload))

        saw_ack = False
        deadline = time.ticks_add(time.ticks_ms(), self.timeout_ms)

        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            typ, data = self._read_frame()
            if typ == "ACK":
                saw_ack = True
                continue
            if typ == "DATA":
                if len(data) < 2:
                    continue
                if data[0] != PN532TOHOST:
                    continue
                resp = data[1]
                if resp != ((cmd + 1) & 0xFF):
                    raise OSError("PN532 unexpected resp 0x%02X" % resp)
                return data[2:]

        if saw_ack:
            raise OSError("PN532 got ACK but no DATA")
        raise OSError("PN532 no response")

    def sam_config(self):
        self._command(CMD_SAMCONFIGURATION, bytes([0x01, 20, 0]))

    def firmware(self):
        r = self._command(CMD_GET_FIRMWARE_VERSION)
        if len(r) < 4:
            raise OSError("FW short")
        return r[0], r[1], r[2], r[3]

    def scan_uid(self):
        r = self._command(CMD_INLISTPASSIVETARGET, bytes([0x01, 0x00]))
        if not r or r[0] == 0:
            return None
        if len(r) < 6:
            return None
        uid_len = r[5]
        uid = r[6:6+uid_len]
        return uid if len(uid) == uid_len else None
