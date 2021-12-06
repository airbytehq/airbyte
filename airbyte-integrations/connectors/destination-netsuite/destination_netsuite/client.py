
from destination_netsuite.netsuite.configuration import Config, TokenAuth
from typing import Any, Iterable, List, Mapping, Tuple, Union

class NetsuiteClient:

    def __init__(self, base_url: str, consumer_key: str, consumer_secret: str, token_id: str, token_secret: str):
        self.config = Config(
            base_url=base_url,
            token_auth=TokenAuth(
                token_id=token_id,
                token_secret=token_secret,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret
            )
        )

