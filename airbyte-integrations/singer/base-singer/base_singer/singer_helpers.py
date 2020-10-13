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
from dataclasses import dataclass

def to_json(string):
    try:
        return json.loads(string)
    except ValueError as e:
        return False


@dataclass
class Catalogs:
    singer_catalog: object
    airbyte_catalog: AirbyteCatalog


class SingerHelper:
    @staticmethod
    def spec_from_file(spec_path) -> AirbyteSpec:
        with open(spec_path) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    @staticmethod
    def get_catalogs(logger, shell_command, singer_transform=(lambda catalog: catalog), airbyte_transform=(lambda catalog: catalog)) -> Catalogs:
        completed_process = subprocess.run(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)

        for line in completed_process.stderr.splitlines():
            logger(line, "ERROR")

        airbyte_streams = []
        singer_catalog = singer_transform(json.loads(completed_process.stdout))

        for stream in singer_catalog.get("streams"):
            name = stream.get("stream")
            schema = stream.get("schema").get("properties")

            # todo: figure out how to serialize an object with an items key in python_jsonschema_objects
            if name == "subscriptions":
                del schema["items"]

            airbyte_streams += [AirbyteStream(name=name, schema=schema)]

        airbyte_catalog = airbyte_transform(AirbyteCatalog(streams=airbyte_streams))

        return Catalogs(singer_catalog=singer_catalog, airbyte_catalog=airbyte_catalog)

    @staticmethod
    def read(logger, shell_command, is_message=(lambda x: True), transform=(lambda x: x)) -> Generator[AirbyteMessage, None, None]:
        with subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as p:
            for line_tuple in zip(p.stdout, p.stderr):
                out_line = line_tuple[0]
                err_line = line_tuple[1]

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
                                out_record = AirbyteRecordMessage(
                                    stream=stream_name,
                                    data=transformed_json["record"],
                                    emitted_at=int(datetime.now().timestamp()) * 1000)
                                out_message = AirbyteMessage(type="RECORD", record=out_record)
                                yield transform(out_message)
                    elif out_line:
                        logger(out_line, "INFO")

                if err_line:
                    logger(err_line, "ERROR")
