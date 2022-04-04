import base64
import binascii
from typing import Any, Union

try:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurve
    from cryptography.hazmat.primitives.asymmetric.utils import (
        decode_dss_signature,
        encode_dss_signature,
    )
except ModuleNotFoundError:
    EllipticCurve = Any  # type: ignore


def force_bytes(value: Union[str, bytes]) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    elif isinstance(value, bytes):
        return value
    else:
        raise TypeError("Expected a string value")


def base64url_decode(input: Union[str, bytes]) -> bytes:
    if isinstance(input, str):
        input = input.encode("ascii")

    rem = len(input) % 4

    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


def base64url_encode(input: bytes) -> bytes:
    return base64.urlsafe_b64encode(input).replace(b"=", b"")


def to_base64url_uint(val: int) -> bytes:
    if val < 0:
        raise ValueError("Must be a positive integer")

    int_bytes = bytes_from_int(val)

    if len(int_bytes) == 0:
        int_bytes = b"\x00"

    return base64url_encode(int_bytes)


def from_base64url_uint(val: Union[str, bytes]) -> int:
    if isinstance(val, str):
        val = val.encode("ascii")

    data = base64url_decode(val)
    return int.from_bytes(data, byteorder="big")


def number_to_bytes(num: int, num_bytes: int) -> bytes:
    padded_hex = "%0*x" % (2 * num_bytes, num)
    return binascii.a2b_hex(padded_hex.encode("ascii"))


def bytes_to_number(string: bytes) -> int:
    return int(binascii.b2a_hex(string), 16)


def bytes_from_int(val: int) -> bytes:
    remaining = val
    byte_length = 0

    while remaining != 0:
        remaining >>= 8
        byte_length += 1

    return val.to_bytes(byte_length, "big", signed=False)


def der_to_raw_signature(der_sig: bytes, curve: EllipticCurve) -> bytes:
    num_bits = curve.key_size
    num_bytes = (num_bits + 7) // 8

    r, s = decode_dss_signature(der_sig)

    return number_to_bytes(r, num_bytes) + number_to_bytes(s, num_bytes)


def raw_to_der_signature(raw_sig: bytes, curve: EllipticCurve) -> bytes:
    num_bits = curve.key_size
    num_bytes = (num_bits + 7) // 8

    if len(raw_sig) != 2 * num_bytes:
        raise ValueError("Invalid signature")

    r = bytes_to_number(raw_sig[:num_bytes])
    s = bytes_to_number(raw_sig[num_bytes:])

    return encode_dss_signature(r, s)
