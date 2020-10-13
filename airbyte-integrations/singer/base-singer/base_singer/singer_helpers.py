import json
import subprocess
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import AirbyteLogMessage
from airbyte_protocol import AirbyteRecordMessage
from airbyte_protocol import AirbyteStateMessage
from airbyte_protocol import AirbyteStream
from typing import Generator
from datetime import datetime


# helper to delegate input and output to a piped command
# todo: add error handling (make sure the overall tap fails if there's a failure in here)

valid_log_types = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]


def log_line(line, default_level):
    split_line = line.split()
    first_word = next(iter(split_line), None)
    if first_word in valid_log_types:
        log_level = first_word
        rendered_line = " ".join(split_line[1:])
    else:
        log_level = default_level
        rendered_line = line
    log_record = AirbyteLogMessage(level=log_level, message=rendered_line)
    log_message = AirbyteMessage(type="LOG", log=log_record)
    print(log_message.serialize())


def to_json(string):
    try:
        return json.loads(string)
    except ValueError as e:
        return False


class SingerHelper:
    @staticmethod
    def spec_from_file(spec_path) -> AirbyteSpec:
        with open(spec_path) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)


    @staticmethod
    def discover(shell_command, transform=(lambda catalog: catalog)) -> AirbyteCatalog:
        completed_process = subprocess.run(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)

        for line in completed_process.stderr.splitlines():
            log_line(line, "ERROR")

        airbyte_streams = []
        obj = json.loads(completed_process.stdout)

        for stream in obj.get("streams"):
            name = stream.get("stream")
            schema = stream.get("schema").get("properties")
            airbyte_streams += [AirbyteStream(name=name, schema=schema)]

        catalog = AirbyteCatalog(streams=airbyte_streams)

        return transform(catalog)

    @staticmethod
    def read(shell_command, is_message=(lambda x: True), transform=(lambda x: x)) -> Generator[AirbyteMessage, None, None]:
        with subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as p:
            # todo: generate combined schema message from discovery and reading the catalog
            for tuple in zip(p.stdout, p.stderr):
                out_line = tuple[0]
                err_line = tuple[1]

                if out_line:
                    out_json = to_json(out_line)
                    if out_json is not None and is_message(out_json):
                        transformed_json = transform(out_json)
                        if transformed_json is not None:
                            if transformed_json.get('type') == "SCHEMA":
                                pass
                            elif transformed_json.get('type') == "STATE":
                                out_record = AirbyteStateMessage(data=transformed_json["value"])
                                out_message = AirbyteMessage(type="STATE", state=out_record)
                                yield transform(out_message)
                            else:
                                # todo: check that messages match the discovered schema
                                stream_name = transformed_json["stream"]
                                out_record = AirbyteRecordMessage(stream=stream_name, data=transformed_json["record"], emitted_at=str(datetime.now()))
                                out_message = AirbyteMessage(type="RECORD", record=out_record)
                                yield transform(out_message)
                    elif out_line:
                        log_line(out_line, "INFO")

                if err_line:
                    log_line(err_line, "ERROR")
