from source import Source
from integration import AirbyteSpec
from integration import AirbyteCheckResponse
from integration import AirbyteSchema
import subprocess
import urllib.request


class SourceImplementation(Source):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        with open("/airbyte/spec.json") as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    def check(self, logger, config) -> AirbyteCheckResponse:
        code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
        return AirbyteCheckResponse(code == 200, {})

    def discover(self, logger, config) -> AirbyteSchema:
        completed_process = subprocess.run("tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # todo: how do we propagate failure with completed_process.returncode != 0?
        return AirbyteSchema(completed_process.stdout)

    # todo: should the config still be the filename or rendered filename or the actual string?
    # should each read write that to a temp file?
    # https://docs.python.org/3/library/tempfile.html
    # process=subprocess.Popen([PathToProcess],stdin=subprocess.PIPE,stdout=subprocess.PIPE);
    # process.stdin.write("\n")
    # todo: handle state
    def read(self, logger, rendered_config_path, state=None):
        with subprocess.Popen(f"tap-exchangeratesapi --config {rendered_config_path}", shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                yield (line)
