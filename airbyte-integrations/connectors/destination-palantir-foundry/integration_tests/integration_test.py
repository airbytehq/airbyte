import json
import logging
import time
import unittest
import uuid
from typing import Optional, List, Dict, Any, Tuple

from airbyte_protocol.models import Status, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, AirbyteStream, SyncMode, \
    DestinationSyncMode, AirbyteMessage, Type, AirbyteStateMessage, AirbyteStreamState, StreamDescriptor, \
    AirbyteRecordMessage
from mockito import unstub

from destination_palantir_foundry import DestinationPalantirFoundry
from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.compass import Compass
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.foundry_api.service_factory import FoundryServiceFactory
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalog
from destination_palantir_foundry.foundry_api.stream_proxy import StreamProxy
from destination_palantir_foundry.utils.project_helper import ProjectHelper
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_writer import FoundryStreamWriter
from integration_tests.test_schema_and_records import JSON_SCHEMA_ALL_DATA_TYPES, SAMPLE_RECORDS


def get_current_milliseconds():
    return int(time.time() * 1000)


def load_config():
    with open("../secrets/config.json", "r") as f:
        return json.loads(f.read())


INCREMENTAL_STREAM_NAME = "incremental_stream"


def _get_configured_catalog_incremental(namespace: str):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=INCREMENTAL_STREAM_NAME,
                    namespace=namespace,
                    json_schema=JSON_SCHEMA_ALL_DATA_TYPES,
                    supported_sync_modes=[SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _get_state(namespace: Optional[str], stream: str, state: int) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"fake_state": state}, stream=AirbyteStreamState(
        stream_descriptor=StreamDescriptor(namespace=namespace, name=stream))))


def _record(namespace: Optional[str], stream_name: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream_name, namespace=namespace, data=data, emitted_at=get_current_milliseconds())
    )


class TestDestinationPalantirFoundry(unittest.TestCase):

    def setUp(self):
        self.raw_config = load_config()
        self.config = FoundryConfig.from_raw(self.raw_config)
        self.destination = DestinationPalantirFoundry()
        self.logger = logging.getLogger("airbyte")

        auth = ConfidentialClientAuthFactory().create(self.config, FoundryStreamWriter.SCOPES)
        auth.sign_in_as_service_user()

        self.service_factory = FoundryServiceFactory(self.raw_config["host"], auth)

    def tearDown(self):
        unstub()

    def test_check_validConfig_succeeds(self):
        outcome = self.destination.check(self.logger, self.raw_config)
        self.assertEqual(outcome.status, Status.SUCCEEDED)

    def test_check_invalidConfig_fails(self):
        invalid_config = {**self.raw_config, "host": "invalid_host"}
        outcome = self.destination.check(self.logger, invalid_config)
        self.assertEqual(outcome.status, Status.FAILED)

    def test_write_incrementalStreamAppend_appendsData(self):
        test_namespace = str(uuid.uuid4())

        state_message = _get_state(test_namespace, INCREMENTAL_STREAM_NAME, 1)

        catalog = _get_configured_catalog_incremental(test_namespace)
        stream = catalog.streams[0].stream

        output_states = list(self.destination.write(
            self.raw_config, catalog,
            [*[_record(stream.namespace, stream.name, data) for data in SAMPLE_RECORDS], state_message]
        ))

        self.assertEqual(len(output_states), 1)
        self.assertEqual(state_message, output_states[0])

        records = self._get_stream_records(stream.namespace, stream.name)

        self.assertEqual(len(records), len(SAMPLE_RECORDS))

        state_message_2 = _get_state(test_namespace, INCREMENTAL_STREAM_NAME, 2)
        output_states_2 = list(self.destination.write(
            self.raw_config, catalog,
            [*[_record(stream.namespace, stream.name, data) for data in SAMPLE_RECORDS], state_message_2]
        ))

        self.assertEqual(len(output_states_2), 1)
        self.assertEqual(state_message_2, output_states_2[0])

        records_2 = self._get_stream_records(stream.namespace, stream.name)

        self.assertEqual(len(records_2), len(SAMPLE_RECORDS) * 2)

        self._delete_stream(stream.namespace, stream.name)

    def _get_stream_records(self, namespace: Optional[str], stream_name: str) -> List[Dict[str, Any]]:
        stream_proxy: StreamProxy = self.service_factory.stream_proxy()

        dataset_rid, view_rid = self._get_stream_dataset_and_view_rids(namespace, stream_name)

        return [record.value for record in stream_proxy.get_records(dataset_rid, view_rid, 100).records]

    def _delete_stream(self, namespace: Optional[str], stream_name: str) -> None:
        compass: Compass = self.service_factory.compass()
        stream_catalog: StreamCatalog = self.service_factory.stream_catalog()

        dataset_rid, _ = self._get_stream_dataset_and_view_rids(namespace, stream_name)

        stream_catalog.delete_stream(dataset_rid)
        compass.delete_permanently([dataset_rid])

    def _get_stream_dataset_and_view_rids(self, namespace: Optional[str], stream_name: str) -> Tuple[str, str]:
        project_helper = ProjectHelper(self.service_factory.compass())
        stream_catalog: StreamCatalog = self.service_factory.stream_catalog()

        stream_dataset_rid = project_helper.maybe_get_resource_by_name(
            self.config.destination_config.project_rid,
            get_foundry_resource_name(namespace, stream_name)
        ).rid

        stream_view_rid = stream_catalog.get_stream(stream_dataset_rid).root.view.viewRid

        return stream_dataset_rid, stream_view_rid
