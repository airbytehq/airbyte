# don't valid it by auto-linters because this file is used for testing
import pathlib
import os



LONG_STRING = """aaaaaaaaaaaaaaaaaaaaaaaaaawwwwwwwwwwwwwwwwwwwwwwwww mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm mmmmmmmmmmmmmm      wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"""


def fake_func() -> str:
    return 1000


def fake_func(i):
   return i * 10
