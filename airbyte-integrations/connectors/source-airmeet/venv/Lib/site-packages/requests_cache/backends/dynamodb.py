"""DynamoDB cache backend. For usage details, see :ref:`Backends: DynamoDB <dynamodb>`.

.. automodsumm:: requests_cache.backends.dynamodb
   :classes-only:
   :nosignatures:
"""

from typing import Iterable, Optional

import boto3
from boto3.dynamodb.types import Binary
from boto3.resources.base import ServiceResource
from botocore.exceptions import ClientError

from requests_cache.backends.base import VT

from .._utils import get_valid_kwargs
from ..serializers import SerializerType, dynamodb_document_serializer
from . import BaseCache, BaseStorage, DictStorage


class DynamoDbCache(BaseCache):
    """DynamoDB cache backend.
    By default, responses are only partially serialized into a DynamoDB-compatible document format.

    Args:
        table_name: DynamoDB table name
        connection: :boto3:`DynamoDB Resource <services/dynamodb/service-resource/index.html#service-resource>`
            object to use instead of creating a new one
        ttl: Use DynamoDB TTL to automatically remove expired items
        kwargs: Additional keyword arguments for :py:meth:`~boto3.session.Session.resource`
    """

    def __init__(
        self,
        table_name: str = 'http_cache',
        *,
        ttl: bool = True,
        connection: Optional[ServiceResource] = None,
        decode_content: bool = True,
        serializer: Optional[SerializerType] = None,
        **kwargs,
    ):
        super().__init__(cache_name=table_name, **kwargs)
        skwargs = {'serializer': serializer, **kwargs} if serializer else kwargs
        self.responses = DynamoDbDict(
            table_name,
            ttl=ttl,
            connection=connection,
            decode_content=decode_content,
            **skwargs,
        )
        # Redirects will be only stored in memory and not persisted
        self.redirects: BaseStorage[str, str] = DictStorage()


class DynamoDbDict(BaseStorage):
    """A dictionary-like interface for DynamoDB table

    Args:
        table_name: DynamoDB table name
        connection: :boto3:`DynamoDB Resource <services/dynamodb/service-resource/index.html#service-resource>`
            object to use instead of creating a new one
        ttl: Use DynamoDB TTL to automatically remove expired items
        kwargs: Additional keyword arguments for :py:meth:`~boto3.session.Session.resource`
    """

    def __init__(
        self,
        table_name: str,
        ttl: bool = True,
        connection: Optional[ServiceResource] = None,
        serializer: Optional[SerializerType] = dynamodb_document_serializer,
        **kwargs,
    ):
        super().__init__(serializer=serializer, **kwargs)
        connection_kwargs = get_valid_kwargs(
            boto3.Session.__init__, kwargs, extras=['endpoint_url']
        )
        self.connection = connection or boto3.resource('dynamodb', **connection_kwargs)
        self.table_name = table_name
        self.ttl = ttl

        self._table = self.connection.Table(self.table_name)
        self._create_table()
        if ttl:
            self._enable_ttl()

    def _create_table(self):
        """Create a default table if one does not already exist"""
        try:
            self.connection.create_table(
                AttributeDefinitions=[
                    {'AttributeName': 'key', 'AttributeType': 'S'},
                ],
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'key', 'KeyType': 'HASH'},
                ],
                BillingMode='PAY_PER_REQUEST',
            )
            self._table.wait_until_exists()
        # Ignore error if table already exists
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                raise

    def _enable_ttl(self):
        """Enable TTL, if not already enabled"""
        try:
            self.connection.meta.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={'AttributeName': 'ttl', 'Enabled': True},
            )
        # Ignore error if TTL is already enabled
        except ClientError as e:
            if e.response['Error']['Code'] != 'ValidationException':
                raise

    def __getitem__(self, key):
        result = self._table.get_item(Key={'key': key})
        if 'Item' not in result:
            raise KeyError
        return self.deserialize(key, result['Item']['value'])

    def __setitem__(self, key, value):
        item = {'key': key, 'value': self.serialize(value)}

        # If enabled, set TTL value as a timestamp in unix format
        if self.ttl and getattr(value, 'expires_unix', None):
            item['ttl'] = value.expires_unix

        self._table.put_item(Item=item)

    def __delitem__(self, key):
        response = self._table.delete_item(Key={'key': key}, ReturnValues='ALL_OLD')
        if 'Attributes' not in response:
            raise KeyError

    def __iter__(self):
        # Alias 'key' attribute since it's a reserved keyword
        results = self._table.scan(
            ProjectionExpression='#k',
            ExpressionAttributeNames={'#k': 'key'},
        )
        for item in results['Items']:
            yield item['key']

    def __len__(self):
        """Get the number of items in the table.

        **Note:** This is an estimate, and is updated every 6 hours. A full table scan will use up
        your provisioned throughput, so it's not recommended.
        """
        return self._table.item_count

    def bulk_delete(self, keys: Iterable[str]):
        """Delete multiple keys from the cache. Does not raise errors for missing keys."""
        with self._table.batch_writer() as batch:
            for key in keys:
                batch.delete_item(Key={'key': key})

    def clear(self):
        self.bulk_delete((k for k in self))

    def deserialize(self, key, value: VT):
        """Handle Binary objects from a custom serializer"""
        serialized_value = value.value if isinstance(value, Binary) else value
        return super().deserialize(key, serialized_value)

    # TODO: Support pagination
    def values(self):
        for item in self._table.scan()['Items']:
            yield self.deserialize(item['key'], item['value'])
