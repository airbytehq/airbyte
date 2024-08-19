# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from unittest.mock import Mock

from airbyte_protocol.models import AirbyteCatalog, AirbyteStream, SyncMode
from erd.dbml_assembler import DbmlAssembler, Source
from tests.builder import RelationshipBuilder

_A_STREAM_NAME = "a_stream_name"


class RelationshipsMergerTest(TestCase):
    def setUp(self) -> None:
        self._source = Mock(spec=Source)
        self._source.is_dynamic.return_value = False
        self._assembler = DbmlAssembler()

    def test_given_no_streams_then_database_is_empty(self) -> None:
        dbml = self._assembler.assemble(
            self._source, AirbyteCatalog(streams=[]), {"streams": [RelationshipBuilder(_A_STREAM_NAME).build()]}
        )
        assert not dbml.tables

    def test_given_stream_is_dynamic_then_ignore(self) -> None:
        self._source.is_dynamic.return_value = True
        dbml = self._assembler.assemble(
            self._source,
            AirbyteCatalog(
                streams=[
                    AirbyteStream(
                        name=_A_STREAM_NAME,
                        json_schema={"properties": {}},
                        supported_sync_modes=[SyncMode.full_refresh],
                    )
                ]
            ),
            {"streams": [RelationshipBuilder(_A_STREAM_NAME).build()]},
        )
        assert not dbml.tables

    def test_given_stream_then_populate_table(self) -> None:
        dbml = self._assembler.assemble(
            self._source,
            AirbyteCatalog(
                streams=[
                    AirbyteStream(
                        name=_A_STREAM_NAME,
                        json_schema={
                            "properties": {
                                "a_primary_key": {"type": ["null", "string"]},
                                "an_integer": {"type": ["null", "number"]},
                            }
                        },
                        supported_sync_modes=[SyncMode.full_refresh],
                        source_defined_primary_key=[["a_primary_key"]],
                    )
                ]
            ),
            {"streams": [RelationshipBuilder(_A_STREAM_NAME).build()]},
        )
        assert len(dbml.tables) == 1
        assert len(dbml.tables[0].columns) == 2
        assert dbml.tables[0].columns[0].name == "a_primary_key"
        assert dbml.tables[0].columns[0].pk
        assert dbml.tables[0].columns[1].name == "an_integer"
