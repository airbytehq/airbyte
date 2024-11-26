import msvcrt

from ._config import config


def readchar() -> str:
    """Reads a single character from the input stream.
    Blocks until a character is available."""

    # manual byte decoding because some bytes in windows are not utf-8 encodable.
    return chr(int.from_bytes(msvcrt.getch(), "big"))


def readkey() -> str:
    """Reads the next keypress. If an escaped key is pressed, the full
    sequence is read and returned as noted in `_win_key.py`."""

    ch = readchar()

    if ch in config.INTERRUPT_KEYS:
        raise KeyboardInterrupt

    # if it is a normal character:
    if ch not in "\x00\xe0":
        return ch

    # if it is a scpeal key, read second half:
    ch2 = readchar()

    return "\x00" + ch2
