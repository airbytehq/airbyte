import subprocess
from integration import AirbyteSpec
from integration import AirbyteSchema
from integration import AirbyteMessage
from typing import Generator


# helper to delegate input and output to a piped command
# todo: add error handling (make sure the overall tap fails if there's a failure in here)

def log_line(line):
    first_word = next(iter(line.split()), None)
    if first_word in ['DEBUG', 'ERROR', 'FATAL', 'INFO', 'TRACE', 'WARN']:
        print(line.strip())
    else:
        print("INFO", line.strip())


class SingerHelper:
    @staticmethod
    def spec_from_file(spec_path) -> AirbyteSpec:
        with open(spec_path) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    # todo: support stderr in the discover process
    @staticmethod
    def discover(shell_command, transform=(lambda x: AirbyteSchema(x))) -> AirbyteSchema:
        completed_process = subprocess.run(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)
        return transform(completed_process.stdout)

    @staticmethod
    def read(shell_command, is_message=(lambda x: True), transform=(lambda x: AirbyteMessage(x))) -> Generator[
        AirbyteMessage, None, None]:
        with subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as p:
            for tuple in zip(p.stdout, p.stderr):
                out_line = tuple[0]
                err_line = tuple[1]

                if out_line:
                    if is_message(out_line):
                        message = transform(out_line)
                        if message is not None:
                            yield transform(out_line)
                    else:
                        log_line(out_line)

                if err_line:
                    log_line(err_line)
