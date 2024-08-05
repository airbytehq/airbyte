from __future__ import annotations
from avro.io import BinaryEncoder, DatumWriter

import io
import json
from google.api_core.exceptions import NotFound
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding
from google.cloud import pubsub_v1

from snoop import logger
import typing

if typing.TYPE_CHECKING:
    import avro

BATCH_SETTINGS = pubsub_v1.types.BatchSettings(
    max_latency=10,  # 10 seconds
)

def publish_to_topic(project_id: str, topic_id: str, record: dict, avro_schema: avro.Schema):
    
    publisher_client = PublisherClient(BATCH_SETTINGS)

    topic_path = publisher_client.topic_path(project_id, topic_id)

    try:
        # Get the topic encoding type.
        topic = publisher_client.get_topic(request={"topic": topic_path})
        encoding = topic.schema_settings.encoding
        if encoding != Encoding.BINARY:
            logger.error(f"Unsupported encoding type: {encoding}. Abort sending the message.")
            return
        
        writer = DatumWriter(avro_schema)
        bout = io.BytesIO()
        encoder = BinaryEncoder(bout)
        writer.write(record, encoder)
        data = bout.getvalue()
        return publisher_client.publish(topic_path, data)

    except NotFound:
        logger.error(f"{topic_id} not found.")