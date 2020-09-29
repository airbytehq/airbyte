from singer_source import SingerSource
from singer_integration import AirbyteSpec


class SourceImplementation(SingerSource):
    def __init__(self):
        print("working...")
        pass

    def spec(self) -> AirbyteSpec:
        print("custom value")
        pass