# don't valid it by auto-linters becaise this file is used for testing
import os
from pathlib import Path

LONG_STRING = """aaaaaaaaaaaaaaaa"""


def func() -> bool:
    return Path(os.getcwd()).is_dir() is True


def func2(i: int) -> int:
    return i * 10
