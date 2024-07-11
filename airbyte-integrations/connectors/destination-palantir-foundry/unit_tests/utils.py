from mockito import ANY, when
import logging


def stub_logger(logger: logging.Logger):
    when(logger).info(...).thenReturn(None)
    when(logger).warn(...).thenReturn(None)
