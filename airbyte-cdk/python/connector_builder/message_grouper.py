from typing import Iterable, Iterator

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer


class MessageGrouper:

    def get_message_groups(self, messages: Iterator[AirbyteMessage], schema_inferrer: SchemaInferrer, limit: int) -> Iterable: #FIXME: set right return type
        pass
