import logging

# todo: add type hints

class AirbyteSpec():
    pass


class AirbyteCheckResponse():
    pass


class AirbyteSchema():
    pass


class SingerIntegration:
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        raise Exception("invalid")

    # CONFIG
    def read_config(self):
        raise Exception("invalid")

    def check(self, logger, config) -> AirbyteCheckResponse:
        raise Exception("invalid")

    def discover(self, logger, config) -> AirbyteSchema:
        raise Exception("invalid")
