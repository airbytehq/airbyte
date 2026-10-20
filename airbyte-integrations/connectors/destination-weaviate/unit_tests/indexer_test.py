#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from collections import defaultdict
from unittest.mock import ANY, MagicMock, Mock, call, patch

from destination_weaviate.config import (
    BearerTokenAuth,
    ClientCredentialsAuth,
    GrpcChannelOption,
    Header,
    NoAuth,
    TokenAuth,
    UsernamePasswordAuth,
    WeaviateIndexingConfigModel,
)
from destination_weaviate.indexer import WeaviateIndexer, WeaviatePartialBatchError

from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.models import AirbyteRecordMessage, DestinationSyncMode


def _property(name):
    prop = Mock()
    prop.name = name
    return prop


def _schema(property_names, multi_tenancy=False):
    schema = Mock()
    schema.properties = [_property(name) for name in property_names]
    schema.multi_tenancy_config.enabled = multi_tenancy
    return schema


def _chunk(content, embedding, metadata):
    return Chunk(
        page_content=content,
        embedding=embedding,
        metadata=metadata,
        record=AirbyteRecordMessage(stream="test", data=metadata, emitted_at=0),
    )


class TestWeaviateIndexer(unittest.TestCase):
    def setUp(self):
        self.config = WeaviateIndexingConfigModel(
            host="https://test-host:12345", auth=TokenAuth(mode="token", token="abc")
        )  # Setup your config here
        self.indexer = WeaviateIndexer(self.config)
        mock_catalog = Mock()
        mock_stream = Mock()
        mock_stream.stream.name = "test"
        mock_stream.destination_sync_mode = DestinationSyncMode.append
        self.mock_stream = mock_stream
        mock_catalog.streams = [mock_stream]
        self.mock_catalog = mock_catalog

    def _mock_client(self, classes=None):
        mock_client = MagicMock()
        mock_client.collections.list_all.return_value = classes or {}
        mock_client.batch.failed_objects = []
        self.indexer.client = mock_client
        return mock_client

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_successful_check(self, MockConnect):
        self.assertIsNone(self.indexer.check())
        MockConnect.return_value.close.assert_called_once()
        self.assertFalse(hasattr(self.indexer, "client"))

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_failed_check_due_to_exception(self, MockConnect):
        MockConnect.side_effect = Exception("Random exception")
        self.assertIsNotNone(self.indexer.check())

    @patch("destination_weaviate.indexer.os.environ")
    def test_failed_check_due_to_cloud_env_and_no_https_host(self, mock_os_environ):
        mock_os_environ.get.return_value = "cloud"
        self.indexer.config.host = "http://example.com"
        self.assertEqual(self.indexer.check(), "Host must start with https:// and authentication must be enabled on cloud deployment.")

    @patch("destination_weaviate.indexer.os.environ")
    def test_failed_check_due_to_cloud_env_and_no_auth(self, mock_os_environ):
        mock_os_environ.get.return_value = "cloud"
        self.indexer.config.host = "http://example.com"
        self.indexer.config.auth = NoAuth(mode="no_auth")
        self.assertEqual(self.indexer.check(), "Host must start with https:// and authentication must be enabled on cloud deployment.")

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_with_explicit_ports(self, MockConnect):
        self.indexer._create_client()
        kwargs = MockConnect.call_args.kwargs
        self.assertEqual(
            (kwargs["http_host"], kwargs["http_port"], kwargs["http_secure"]),
            ("test-host", 12345, True),
        )
        self.assertEqual((kwargs["grpc_host"], kwargs["grpc_port"], kwargs["grpc_secure"]), ("test-host", 50051, True))
        self.assertEqual(kwargs["auth_credentials"].api_key, "abc")

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_to_weaviate_cloud_grpc_endpoint(self, MockConnect):
        # The console shows the REST endpoint without a scheme, so bare hostnames and URLs must both work
        for host, expected_http, expected_grpc in [
            (
                "https://my-cluster.c0.europe-west3.gcp.weaviate.cloud",
                "my-cluster.c0.europe-west3.gcp.weaviate.cloud",
                "grpc-my-cluster.c0.europe-west3.gcp.weaviate.cloud",
            ),
            (
                "my-cluster.c0.europe-west3.gcp.weaviate.cloud",
                "my-cluster.c0.europe-west3.gcp.weaviate.cloud",
                "grpc-my-cluster.c0.europe-west3.gcp.weaviate.cloud",
            ),
            ("https://my-sandbox-abc123.weaviate.network", "my-sandbox-abc123.weaviate.network", "my-sandbox-abc123.grpc.weaviate.network"),
        ]:
            self.indexer.config.host = host
            self.indexer._create_client()
            kwargs = MockConnect.call_args.kwargs
            self.assertEqual((kwargs["http_host"], kwargs["http_port"], kwargs["http_secure"]), (expected_http, 443, True))
            self.assertEqual((kwargs["grpc_host"], kwargs["grpc_port"], kwargs["grpc_secure"]), (expected_grpc, 443, True))

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_to_local_without_tls(self, MockConnect):
        self.indexer.config.host = "http://localhost"
        self.indexer.config.auth = NoAuth(mode="no_auth")
        self.indexer._create_client()
        kwargs = MockConnect.call_args.kwargs
        self.assertEqual((kwargs["http_host"], kwargs["http_port"], kwargs["http_secure"]), ("localhost", 80, False))
        self.assertEqual((kwargs["grpc_host"], kwargs["grpc_port"], kwargs["grpc_secure"]), ("localhost", 50051, False))
        self.assertIsNone(kwargs["auth_credentials"])
        self.assertFalse(kwargs["skip_init_checks"])

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_to_configured_grpc_endpoint(self, MockConnect):
        for grpc_host, expected in [
            ("grpc.example.com:8443", ("grpc.example.com", 8443)),
            ("https://grpc.example.com", ("grpc.example.com", 443)),
            ("grpc.example.com", ("grpc.example.com", 443)),
        ]:
            self.indexer.config.connection.grpc_host = grpc_host
            self.indexer._create_client()
            kwargs = MockConnect.call_args.kwargs
            self.assertEqual((kwargs["grpc_host"], kwargs["grpc_port"]), expected)

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_grpc_tls_override(self, MockConnect):
        for grpc_secure, http_host, expected in [
            ("disabled", "https://test-host", (False, 50051)),
            ("enabled", "http://test-host", (True, 443)),
            ("auto", "http://test-host", (False, 50051)),
        ]:
            self.indexer.config.host = http_host
            self.indexer.config.connection.grpc_secure = grpc_secure
            self.indexer.config.connection.grpc_host = "grpc-host"
            self.indexer._create_client()
            kwargs = MockConnect.call_args.kwargs
            self.assertEqual((kwargs["grpc_secure"], kwargs["grpc_port"]), expected)

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_failed_check_due_to_invalid_host(self, MockConnect):
        self.indexer.config.host = "ftp://my-cluster.weaviate.network"
        self.assertIn("must be a hostname or a URL starting with http:// or https://", self.indexer.check())
        MockConnect.assert_not_called()

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_default_additional_config(self, MockConnect):
        self.indexer._create_client()
        additional_config = MockConnect.call_args.kwargs["additional_config"]
        self.assertEqual((additional_config.timeout.init, additional_config.timeout.query, additional_config.timeout.insert), (2, 30, 90))
        self.assertIsNone(additional_config.proxies)
        self.assertIsNone(additional_config.grpc_config)
        self.assertFalse(additional_config.trust_env)
        self.assertEqual(additional_config.connection.session_pool_maxsize, 100)

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_passes_all_connection_options(self, MockConnect):
        connection = self.indexer.config.connection
        connection.timeout_init = 5
        connection.timeout_query = 60
        connection.timeout_insert = 300
        connection.skip_init_checks = True
        connection.trust_env = True
        connection.https_proxy = "http://proxy:3128"
        connection.grpc_proxy = "http://grpc-proxy:3128"
        connection.session_pool_connections = 5
        connection.session_pool_maxsize = 50
        connection.session_pool_max_retries = 7
        connection.session_pool_timeout = 9
        connection.grpc_channel_options = [
            GrpcChannelOption(name="grpc.keepalive_time_ms", value="10000"),
            GrpcChannelOption(name="grpc.lb_policy_name", value="round_robin"),
        ]
        self.indexer._create_client()
        kwargs = MockConnect.call_args.kwargs
        additional_config = kwargs["additional_config"]
        self.assertTrue(kwargs["skip_init_checks"])
        self.assertEqual((additional_config.timeout.init, additional_config.timeout.query, additional_config.timeout.insert), (5, 60, 300))
        self.assertTrue(additional_config.trust_env)
        self.assertEqual(
            (additional_config.proxies.http, additional_config.proxies.https, additional_config.proxies.grpc),
            (None, "http://proxy:3128", "http://grpc-proxy:3128"),
        )
        pool = additional_config.connection
        self.assertEqual(
            (pool.session_pool_connections, pool.session_pool_maxsize, pool.session_pool_max_retries, pool.session_pool_timeout),
            (5, 50, 7, 9),
        )
        self.assertEqual(
            additional_config.grpc_config.channel_options, [("grpc.keepalive_time_ms", 10000), ("grpc.lb_policy_name", "round_robin")]
        )

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_with_username_password(self, MockConnect):
        self.indexer.config.auth = UsernamePasswordAuth(mode="username_password", username="user", password="pass")
        self.indexer._create_client()
        credentials = MockConnect.call_args.kwargs["auth_credentials"]
        self.assertEqual((credentials.username, credentials.password, credentials.scope), ("user", "pass", None))

        self.indexer.config.auth.scope = "offline_access openid"
        self.indexer._create_client()
        self.assertEqual(MockConnect.call_args.kwargs["auth_credentials"].scope, "offline_access openid")

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_with_client_credentials(self, MockConnect):
        self.indexer.config.auth = ClientCredentialsAuth(mode="client_credentials", client_secret="secret", scope="app/.default")
        self.indexer._create_client()
        credentials = MockConnect.call_args.kwargs["auth_credentials"]
        self.assertEqual((credentials.client_secret, credentials.scope), ("secret", "app/.default"))

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_connects_with_bearer_token(self, MockConnect):
        self.indexer.config.auth = BearerTokenAuth(mode="bearer_token", access_token="access", refresh_token="refresh", expires_in=300)
        self.indexer._create_client()
        credentials = MockConnect.call_args.kwargs["auth_credentials"]
        self.assertEqual((credentials.access_token, credentials.refresh_token, credentials.expires_in), ("access", "refresh", 300))

    @patch("destination_weaviate.indexer.version", return_value="1.2.3")
    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_sends_integration_header_with_additional_headers(self, MockConnect, MockVersion):
        self.indexer.config.additional_headers = [Header(header_key="X-OpenAI-Api-Key", value="key")]
        self.indexer._create_client()
        self.assertEqual(
            MockConnect.call_args.kwargs["headers"],
            {"X-OpenAI-Api-Key": "key", "X-Weaviate-Client-Integration": "airbyte-destination-weaviate/1.2.3"},
        )
        MockVersion.assert_called_with("airbyte-destination-weaviate")

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_that_creates_class(self, MockConnect):
        mock_client = self._mock_client()
        MockConnect.return_value = mock_client
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.collections.create_from_dict.assert_called_with(
            {
                "class": "Test",
                "vectorizer": "none",
                "properties": [
                    {
                        "name": "_ab_record_id",
                        "dataType": ["text"],
                        "description": "Record ID, used for bookkeeping.",
                        "indexFilterable": True,
                        "indexSearchable": False,
                        "tokenization": "field",
                    }
                ],
            }
        )
        mock_client.collections.use.return_value.tenants.create.assert_not_called()

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_that_creates_class_with_multi_tenancy_enabled(self, MockConnect):
        mock_client = self._mock_client()
        MockConnect.return_value = mock_client
        mock_client.collections.use.return_value.tenants.get.return_value = {}
        self.config.tenant_id = "test_tenant"
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.collections.create_from_dict.assert_called_with(
            {
                "class": "Test",
                "multiTenancyConfig": {"enabled": True},
                "vectorizer": "none",
                "properties": [
                    {
                        "name": "_ab_record_id",
                        "dataType": ["text"],
                        "description": "Record ID, used for bookkeeping.",
                        "indexFilterable": True,
                        "indexSearchable": False,
                        "tokenization": "field",
                    }
                ],
            }
        )
        mock_client.collections.use.assert_called_with("Test")
        tenants = mock_client.collections.use.return_value.tenants.create.call_args.args[0]
        self.assertEqual([tenant.name for tenant in tenants], ["test_tenant"])

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_keeps_existing_tenant(self, MockConnect):
        mock_client = self._mock_client({"Test": _schema(["_ab_record_id"], multi_tenancy=True)})
        MockConnect.return_value = mock_client
        mock_client.collections.use.return_value.tenants.get.return_value = {"test_tenant": Mock()}
        self.config.tenant_id = "test_tenant"
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.collections.use.return_value.tenants.create.assert_not_called()

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_with_tenant_only_touches_synced_multi_tenant_classes(self, MockConnect):
        mock_client = self._mock_client(
            {
                "Test": _schema(["_ab_record_id"], multi_tenancy=False),
                "SomeoneElsesClass": _schema(["title"], multi_tenancy=True),
            }
        )
        MockConnect.return_value = mock_client
        self.config.tenant_id = "test_tenant"
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.collections.use.assert_not_called()

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_that_deletes(self, MockConnect):
        schema = _schema(["_ab_stream", "_ab_record_id"])
        mock_client = self._mock_client({"Test": schema})
        MockConnect.return_value = mock_client
        self.mock_stream.destination_sync_mode = DestinationSyncMode.overwrite
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.collections.delete.assert_called_with("Test")
        mock_client.collections.create_from_config.assert_called_with(schema)

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_overwrite_recreates_tenant(self, MockConnect):
        mock_client = self._mock_client({"Test": _schema(["_ab_record_id"], multi_tenancy=True)})
        MockConnect.return_value = mock_client
        mock_client.collections.use.return_value.tenants.get.return_value = {}
        self.config.tenant_id = "test_tenant"
        self.mock_stream.destination_sync_mode = DestinationSyncMode.overwrite
        self.indexer.pre_sync(self.mock_catalog)
        self.assertEqual(
            [name for name, *_ in mock_client.method_calls if name.startswith("collections.")][-3:],
            ["collections.delete", "collections.create_from_config", "collections.use"],
        )
        mock_client.collections.use.return_value.tenants.create.assert_called_once()

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_pre_sync_no_delete_no_overwrite_mode(self, MockConnect):
        mock_client = self._mock_client({"Test": _schema(["_ab_stream", "_ab_record_id"])})
        MockConnect.return_value = mock_client
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.collections.delete.assert_not_called()
        self.assertTrue(self.indexer.has_record_id_metadata["Test"])

    @patch("destination_weaviate.indexer.weaviate.connect_to_custom")
    def test_post_sync_closes_client(self, MockConnect):
        self.indexer.pre_sync(self.mock_catalog)
        self.assertEqual(self.indexer.post_sync(), [])
        MockConnect.return_value.close.assert_called_once()
        self.assertFalse(hasattr(self.indexer, "client"))

    def test_index_deletes_by_record_id(self):
        mock_client = self._mock_client()
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = True
        self.indexer.delete(["some_id", "some_other_id"], None, "test")
        mock_client.collections.use.assert_called_with("Test")
        mock_client.collections.use.return_value.with_tenant.assert_not_called()
        where = mock_client.collections.use.return_value.data.delete_many.call_args.kwargs["where"]
        self.assertEqual((where.target, where.operator.value, where.value), ("_ab_record_id", "ContainsAny", ["some_id", "some_other_id"]))

    def test_index_deletes_by_record_id_with_tenant_id(self):
        mock_client = self._mock_client()
        self.config.tenant_id = "test_tenant"
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = True
        self.indexer.delete(["some_id", "some_other_id"], None, "test")
        mock_client.collections.use.return_value.with_tenant.assert_called_with("test_tenant")
        mock_client.collections.use.return_value.with_tenant.return_value.data.delete_many.assert_called_once()

    def test_delete_with_consistency_level(self):
        mock_client = self._mock_client()
        self.config.consistency_level = "ALL"
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = True
        self.indexer.delete(["some_id"], None, "test")
        with_consistency_level = mock_client.collections.use.return_value.with_consistency_level
        self.assertEqual(with_consistency_level.call_args.args[0].value, "ALL")
        with_consistency_level.return_value.data.delete_many.assert_called_once()

    def test_index_not_delete_no_metadata_field(self):
        mock_client = self._mock_client()
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = False
        self.indexer.delete(["some_id"], None, "test")
        mock_client.collections.use.assert_not_called()

    def test_index_flushes_batch(self):
        mock_client = self._mock_client()
        batch = mock_client.batch.fixed_size.return_value.__enter__.return_value
        mock_chunk1 = _chunk("some_content", [1, 2, 3], {"someField": "some_value"})
        mock_chunk2 = _chunk("some_other_content", [4, 5, 6], {"someField": "some_value2"})
        self.indexer.index([mock_chunk1, mock_chunk2], None, "test")
        mock_client.batch.fixed_size.assert_called_once_with(batch_size=128, concurrent_requests=1, consistency_level=None)
        chunk1_call = call(
            collection="Test", properties={"someField": "some_value", "text": "some_content"}, uuid=ANY, vector=[1, 2, 3], tenant=None
        )
        chunk2_call = call(
            collection="Test",
            properties={"someField": "some_value2", "text": "some_other_content"},
            uuid=ANY,
            vector=[4, 5, 6],
            tenant=None,
        )
        batch.add_object.assert_has_calls([chunk1_call, chunk2_call], any_order=False)

    def test_index_with_tenant_id(self):
        mock_client = self._mock_client()
        self.config.tenant_id = "test_tenant"
        batch = mock_client.batch.fixed_size.return_value.__enter__.return_value
        self.indexer.index([_chunk("some_content", [1, 2, 3], {"someField": "some_value"})], None, "test")
        self.assertEqual(batch.add_object.call_args.kwargs["tenant"], "test_tenant")

    def test_index_uses_batch_options(self):
        mock_client = self._mock_client()
        self.indexer.config.batch_size = 2
        self.indexer.config.concurrent_requests = 4
        self.indexer.config.consistency_level = "ONE"
        batch = mock_client.batch.fixed_size.return_value.__enter__.return_value
        mock_chunk1 = _chunk("some_content", [1, 2, 3], {"someField": "some_value"})
        mock_chunk2 = _chunk("some_other_content", [4, 5, 6], {"someField": "some_value2"})
        mock_chunk3 = _chunk("third", [7, 8, 9], {"someField": "some_value3"})
        self.indexer.index([mock_chunk1, mock_chunk2, mock_chunk3], None, "test")
        kwargs = mock_client.batch.fixed_size.call_args.kwargs
        self.assertEqual((kwargs["batch_size"], kwargs["concurrent_requests"], kwargs["consistency_level"].value), (2, 4, "ONE"))
        self.assertEqual(batch.add_object.call_count, 3)

    def test_index_on_empty_batch(self):
        mock_client = self._mock_client()
        self.indexer.index([], None, "test")
        assert mock_client.batch.fixed_size.call_count == 0

    def test_index_flushes_batch_and_propagates_error(self):
        mock_client = self._mock_client()
        failed = Mock()
        failed.message = "some_error"
        mock_client.batch.failed_objects = [failed]
        mock_chunk1 = _chunk("some_content", [1, 2, 3], {"someField": "some_value"})
        with self.assertRaisesRegex(WeaviatePartialBatchError, "some_error"):
            self.indexer.index([mock_chunk1], None, "test")
        mock_client.batch.fixed_size.return_value.__exit__.assert_called_once()

    def test_index_flushes_batch_and_normalizes(self):
        mock_client = self._mock_client()
        batch = mock_client.batch.fixed_size.return_value.__enter__.return_value
        mock_chunk = _chunk(
            "some_content",
            [1, 2, 3],
            {
                "someField": "some_value",
                "complex": {"a": [1, 2, 3]},
                "UPPERCASE_NAME": "abc",
                "id": 12,
                "empty_list": [],
                "referral Agency Name": "test1",
                "123StartsWithNumber": "test2",
                "special&*chars": "test3",
                "with spaces": "test4",
                "": "test5",
                "_startsWithUnderscore": "test6",
                "multiple  spaces": "test7",
                "SpecialCharacters!@#": "test8",
            },
        )
        self.indexer.index([mock_chunk], None, "test")
        batch.add_object.assert_called_with(
            collection="Test",
            properties={
                "someField": "some_value",
                "complex": '{"a": [1, 2, 3]}',
                "uPPERCASE_NAME": "abc",
                "text": "some_content",
                "raw_id": 12,
                "referral_Agency_Name": "test1",
                "_123StartsWithNumber": "test2",
                "specialchars": "test3",
                "with_spaces": "test4",
                "_": "test5",
                "_startsWithUnderscore": "test6",
                "multiple__spaces": "test7",
                "specialCharacters": "test8",
            },
            uuid=ANY,
            vector=[1, 2, 3],
            tenant=None,
        )
