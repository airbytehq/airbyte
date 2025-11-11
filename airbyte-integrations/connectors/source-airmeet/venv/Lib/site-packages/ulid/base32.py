from collections.abc import Sequence

from ulid import constants


# The encoding and decoding arithmetics are based on the implementation of RobThree
# https://github.com/RobThree/NUlid/blob/89f5a9fc827d191ae5adafe42547575ed3a47723/NUlid/Ulid.cs#L168

ENCODE: str = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
DECODE: Sequence[int] = [
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x00,
    0x01,
    0x02,
    0x03,
    0x04,
    0x05,
    0x06,
    0x07,
    0x08,
    0x09,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0xFF,
    0x12,
    0x13,
    0xFF,
    0x14,
    0x15,
    0xFF,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0xFF,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0xFF,
    0x12,
    0x13,
    0xFF,
    0x14,
    0x15,
    0xFF,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0xFF,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
]


def encode(binary: bytes) -> str:
    if len(binary) != constants.BYTES_LEN:
        raise ValueError("ULID has to be exactly 16 bytes long")
    return encode_timestamp(binary[: constants.TIMESTAMP_LEN]) + encode_randomness(
        binary[constants.TIMESTAMP_LEN :]
    )


def encode_timestamp(binary: bytes) -> str:
    if len(binary) != constants.TIMESTAMP_LEN:
        raise ValueError("Timestamp value has to be exactly 6 bytes long.")
    lut = ENCODE
    return "".join([
        lut[(binary[0] & 224) >> 5],
        lut[(binary[0] & 31)],
        lut[(binary[1] & 248) >> 3],
        lut[((binary[1] & 7) << 2) | ((binary[2] & 192) >> 6)],
        lut[((binary[2] & 62) >> 1)],
        lut[((binary[2] & 1) << 4) | ((binary[3] & 240) >> 4)],
        lut[((binary[3] & 15) << 1) | ((binary[4] & 128) >> 7)],
        lut[(binary[4] & 124) >> 2],
        lut[((binary[4] & 3) << 3) | ((binary[5] & 224) >> 5)],
        lut[(binary[5] & 31)],
    ])


def encode_randomness(binary: bytes) -> str:
    if len(binary) != constants.RANDOMNESS_LEN:
        raise ValueError("Randomness value has to be exactly 10 bytes long.")
    lut = ENCODE
    return "".join([
        lut[(binary[0] & 248) >> 3],
        lut[((binary[0] & 7) << 2) | ((binary[1] & 192) >> 6)],
        lut[(binary[1] & 62) >> 1],
        lut[((binary[1] & 1) << 4) | ((binary[2] & 240) >> 4)],
        lut[((binary[2] & 15) << 1) | ((binary[3] & 128) >> 7)],
        lut[(binary[3] & 124) >> 2],
        lut[((binary[3] & 3) << 3) | ((binary[4] & 224) >> 5)],
        lut[(binary[4] & 31)],
        lut[(binary[5] & 248) >> 3],
        lut[((binary[5] & 7) << 2) | ((binary[6] & 192) >> 6)],
        lut[(binary[6] & 62) >> 1],
        lut[((binary[6] & 1) << 4) | ((binary[7] & 240) >> 4)],
        lut[((binary[7] & 15) << 1) | ((binary[8] & 128) >> 7)],
        lut[(binary[8] & 124) >> 2],
        lut[((binary[8] & 3) << 3) | ((binary[9] & 224) >> 5)],
        lut[(binary[9] & 31)],
    ])


def decode(encoded: str) -> bytes:
    if len(encoded) != constants.REPR_LEN:
        raise ValueError("Encoded ULID has to be exactly 26 characters long.")
    if any((c not in ENCODE) for c in encoded):
        raise ValueError(f"Encoded ULID can only consist of letters in {ENCODE}.")
    return decode_timestamp(encoded[: constants.TIMESTAMP_REPR_LEN]) + decode_randomness(
        encoded[constants.TIMESTAMP_REPR_LEN :]
    )


def decode_timestamp(encoded: str) -> bytes:
    if len(encoded) != constants.TIMESTAMP_REPR_LEN:
        raise ValueError("ULID timestamp has to be exactly 10 characters long.")
    lut = DECODE
    values: bytes = bytes(encoded, "ascii")
    # https://github.com/ulid/spec?tab=readme-ov-file#overflow-errors-when-parsing-base32-strings
    if lut[values[0]] > 7:  # noqa: PLR2004
        raise ValueError(f"Timestamp value {encoded} is too large and will overflow 128-bits.")
    return bytes([
        ((lut[values[0]] << 5) | lut[values[1]]) & 0xFF,
        ((lut[values[2]] << 3) | (lut[values[3]] >> 2)) & 0xFF,
        ((lut[values[3]] << 6) | (lut[values[4]] << 1) | (lut[values[5]] >> 4)) & 0xFF,
        ((lut[values[5]] << 4) | (lut[values[6]] >> 1)) & 0xFF,
        ((lut[values[6]] << 7) | (lut[values[7]] << 2) | (lut[values[8]] >> 3)) & 0xFF,
        ((lut[values[8]] << 5) | (lut[values[9]])) & 0xFF,
    ])


def decode_randomness(encoded: str) -> bytes:
    if len(encoded) != constants.RANDOMNESS_REPR_LEN:
        raise ValueError("ULID randomness has to be exactly 16 characters long.")
    lut = DECODE
    values = bytes(encoded, "ascii")
    return bytes([
        ((lut[values[0]] << 3) | (lut[values[1]] >> 2)) & 0xFF,
        ((lut[values[1]] << 6) | (lut[values[2]] << 1) | (lut[values[3]] >> 4)) & 0xFF,
        ((lut[values[3]] << 4) | (lut[values[4]] >> 1)) & 0xFF,
        ((lut[values[4]] << 7) | (lut[values[5]] << 2) | (lut[values[6]] >> 3)) & 0xFF,
        ((lut[values[6]] << 5) | (lut[values[7]])) & 0xFF,
        ((lut[values[8]] << 3) | (lut[values[9]] >> 2)) & 0xFF,
        ((lut[values[9]] << 6) | (lut[values[10]] << 1) | (lut[values[11]] >> 4)) & 0xFF,
        ((lut[values[11]] << 4) | (lut[values[12]] >> 1)) & 0xFF,
        ((lut[values[12]] << 7) | (lut[values[13]] << 2) | (lut[values[14]] >> 3)) & 0xFF,
        ((lut[values[14]] << 5) | (lut[values[15]])) & 0xFF,
    ])
