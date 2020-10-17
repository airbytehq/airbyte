import os
import selectors
import subprocess
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import AirbyteRecordMessage
from airbyte_protocol import AirbyteStateMessage
from airbyte_protocol import AirbyteStream
from dataclasses import dataclass
from datetime import datetime
from typing import Generator

import json


def to_json(string):
    try:
        return json.loads(string)
    except ValueError as e:
        return False


def is_field_metadata(metadata):
    if len(metadata.get("breadcrumb")) != 2:
        return False
    else:
        return metadata.get("breadcrumb")[0] != "property"


@dataclass
class Catalogs:
    singer_catalog: object
    airbyte_catalog: AirbyteCatalog


class SingerHelper:
    @staticmethod
    def get_catalogs(logger, shell_command, singer_transform=(lambda catalog: catalog), airbyte_transform=(lambda catalog: catalog)) -> Catalogs:
        completed_process = subprocess.run(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)

        for line in completed_process.stderr.splitlines():
            logger.log_by_prefix(line, "ERROR")

        airbyte_streams = []
        singer_catalog = singer_transform(json.loads(completed_process.stdout))

        for stream in singer_catalog.get("streams"):
            name = stream.get("stream")
            schema = stream.get("schema").get("properties")
            airbyte_streams += [AirbyteStream(name=name, json_schema=schema)]

        airbyte_catalog = airbyte_transform(AirbyteCatalog(streams=airbyte_streams))

        return Catalogs(singer_catalog=singer_catalog, airbyte_catalog=airbyte_catalog)

    @staticmethod
    def read(logger, shell_command, is_message=(lambda x: True), transform=(lambda x: x)) -> Generator[AirbyteMessage, None, None]:
        with subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as p:
            sel = selectors.DefaultSelector()
            sel.register(p.stdout, selectors.EVENT_READ)
            sel.register(p.stderr, selectors.EVENT_READ)

            ok = True
            while ok:
                for key, val1 in sel.select():
                    line = key.fileobj.readline()
                    if not line:
                        ok = False
                    elif key.fileobj is p.stdout:
                        out_json = to_json(line)
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
                        else:
                            logger.log_by_prefix(line, "INFO")
                    else:
                        logger.log_by_prefix(line, "ERROR")

    @staticmethod
    def create_singer_catalog_with_selection(masked_airbyte_catalog, discovered_singer_catalog) -> str:
        combined_catalog_path = os.path.join('singer_rendered_catalog.json')
        masked_singer_streams = []

        stream_to_airbyte_schema = {}
        for stream in masked_airbyte_catalog["streams"]:
            stream_to_airbyte_schema[stream.get("name")] = stream

        for singer_stream in discovered_singer_catalog.get("streams"):
            if singer_stream.get("stream") in stream_to_airbyte_schema:
                new_metadatas = []
                metadatas = singer_stream.get("metadata")
                for metadata in metadatas:
                    new_metadata = metadata
                    new_metadata["metadata"]["selected"] = True
                    if not is_field_metadata(new_metadata):
                        new_metadata["metadata"]["forced-replication-method"] = "FULL_TABLE"
                    new_metadatas += [new_metadata]
                singer_stream["metadata"] = new_metadatas

            masked_singer_streams += [singer_stream]

        combined_catalog = {"streams": masked_singer_streams}
        with open(combined_catalog_path, 'w') as fh:
            fh.write(json.dumps(combined_catalog))

        return combined_catalog_path
