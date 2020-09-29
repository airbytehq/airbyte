from integration import Integration


class Source(SingerIntegration):
    def __init__(self):
        pass

    # Iterator<AirbyteMessage>
    def read(self, logger, config, state=None):
        raise Exception("invalid")
