from destination_netsuite.client import NetsuiteClient
from destination_netsuite.netsuite.configuration import Config, TokenAuth
from importlib import import_module
from collections import Mapping
import requests


class NetsuiteWriter:
    pass

def create_record_writer(
        base_url: str,
        consumer_key: str, 
        consumer_secret: str, 
        token_id: str, 
        token_secret: str,
        record_type: str, 
        operation: str #TODO: still working on how to dynamically call an operation
    ):
    """
    dynamically call service class by name
    """
    config = Config(
            base_url=base_url,
            token_auth=TokenAuth(
                token_id=token_id,
                token_secret=token_secret,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret
            )
        )
    try:
        module = import_module("destination_netsuite.netsuite.service")
        return getattr(module, record_type)(config=config)
    except (ImportError, AttributeError) as e:
        raise e  
