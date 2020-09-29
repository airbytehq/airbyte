from integration import SingerIntegration


class SingerSource(SingerIntegration):
    def __init__(self):
        pass

    # Iterator<AirbyteMessage>
    def read(self, logger, config, state=None):
        raise Exception("invalid")
