import weaviate

from typing import Any, Mapping
import uuid


class Client:
    def __init__(self, config: Mapping[str, Any]):
        self.client = self.get_weaviate_client(config)
        self.config = config
        self.batch_size = 100

    def queue_write_operation(self, stream_name: str, record: Mapping):
        # TODO need to handle case where original DB ID is not a UUID
        id = ""
        if record.get('id'):
            id = record.get("id")
            del record["id"]
        else:
            id = uuid.uuid4()

        self.client.batch.add_data_object(record, stream_name, id)
        if self.client.batch.num_objects() >= self.batch_size:
            self.client.batch.create_objects()

    def flush(self):
        self.client.batch.create_objects()

    @staticmethod
    def get_weaviate_client(config: Mapping[str, Any]) -> weaviate.Client:
        url, username, password = config.get("url"), config.get("username"), config.get("password")

        if username and not password:
            raise Exception("Password is required when username is set")
        if password and not username:
            raise Exception("Username is required when password is set")

        if username and password:
            credentials = weaviate.auth.AuthClientPassword(username, password)
            return weaviate.Client(url=url, auth_client_secret=credentials)
        return weaviate.Client(url=url, timeout_config=(2, 2))
