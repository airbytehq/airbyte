import logging
import subprocess
from integration import AirbyteSpec
from integration import AirbyteSchema
from integration import AirbyteMessage

# helper to delegate input and output to a piped command
# todo: add error handling (make sure the overall tap fails if there's a failure in here)

class SingerHelper:
    @staticmethod
    def spec_from_file(spec_path) -> AirbyteSpec:
        with open(spec_path) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    @staticmethod
    def discover(shell_command, transform=(lambda x: AirbyteSchema(x))) -> AirbyteSchema:
        completed_process = subprocess.run(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)
        return transform(completed_process.stdout)

    @staticmethod
    def read(shell_command, is_message=(lambda x: True), transform=(lambda x: AirbyteMessage(x))):
        with subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, bufsize=(int(1E6)),
                              universal_newlines=True) as p:
            for line in p.stdout:
                if is_message(line):
                    message = transform(line)
                    if message is not None:
                        yield transform(line)
                else:
                    logging.info(line)
