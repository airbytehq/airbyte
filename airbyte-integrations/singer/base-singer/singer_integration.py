import logging

# todo: add type hints

class SingerIntegration:
    def __init__(self):
        pass

    # AirbyteSpec
    def spec(self):
        pass

    # CONFIG
    def read_config(self):
        pass

    # AirbyteCheckResponse
    def check(self, logger, config):
        pass

    # AirbyteSchema
    def discover(self, logger, config):
        pass
