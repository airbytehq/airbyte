from source import Source
from integration import AirbyteSpec


class SourceImplementation(Source):
    def __init__(self):
        print("working...")
        pass

    def spec(self) -> AirbyteSpec:
        print("custom value")
        pass

    def read_config(self):
            raise Exception("invalid")

    def check(self, logger, config) -> AirbyteCheckResponse:
        raise Exception("invalid")

    def discover(self, logger, config) -> AirbyteSchema:
        raise Exception("invalid")

    # todo: should the config still be the filename or rendered filename or the actual string?
    # should each read write that to a temp file?
    # https://docs.python.org/3/library/tempfile.html
    def read(self, logger, config, state=None):
        # process=subprocess.Popen([PathToProcess],stdin=subprocess.PIPE,stdout=subprocess.PIPE);
        # process.stdin.write("\n")
        raise Exception("invalid")

