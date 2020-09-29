from source import Source
from integration import AirbyteSpec


class SourceImplementation(Source):
    def __init__(self):
        print("working...")
        pass

    def spec(self) -> AirbyteSpec:
        print("custom value")
        pass