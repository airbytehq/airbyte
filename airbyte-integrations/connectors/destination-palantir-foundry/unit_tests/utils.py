import logging

from mockito import when


def stub_logger(logger: logging.Logger):
    when(logger).info(...).thenReturn(None)
    when(logger).warn(...).thenReturn(None)
