# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
import json
from pathlib import Path
from typing import Any

import dpath
import google.generativeai as genai  # type: ignore  # missing library stubs or py.typed marker
from airbyte_protocol.models import AirbyteCatalog  # type: ignore  # missing library stubs or py.typed marker
from erd.dbml_assembler import DbmlAssembler, Source
from erd.relationships import Relationships, RelationshipsMerger
from markdown_it import MarkdownIt
from pydbml.renderer.dbml.default import DefaultDBMLRenderer  # type: ignore  # missing library stubs or py.typed marker


class ErdService:
    def __init__(self, source_technical_name: str, source_path: Path) -> None:
        self._source_technical_name = source_technical_name
        self._source_path = source_path
        self._model = genai.GenerativeModel("gemini-1.5-flash")

        if not self._discovered_catalog_path.exists():
            raise ValueError(f"Could not find discovered catalog at path {self._discovered_catalog_path}")

    def generate_estimated_relationships(self) -> None:
        normalized_catalog = self._normalize_schema_catalog(self._get_catalog())
        estimated_relationships = self._get_relations_from_gemini(source_name=self._source_path.name, catalog=normalized_catalog)
        with open(self._estimated_relationships_file, "w") as estimated_relationship_file:
            json.dump(estimated_relationships, estimated_relationship_file, indent=4)

    def write_dbml_file(self) -> None:
        database = DbmlAssembler().assemble(
            Source(self._source_path, self._source_technical_name),
            self._get_catalog(),
            RelationshipsMerger().merge(
                self._get_relationships(self._estimated_relationships_file), self._get_relationships(self._confirmed_relationships_file)
            ),
        )

        with open(self._erd_folder / "source.dbml", "w") as f:
            f.write(DefaultDBMLRenderer.render_db(database))

    @staticmethod
    def _normalize_schema_catalog(catalog: AirbyteCatalog) -> dict[str, Any]:
        """
        Foreign key cannot be of type object or array, therefore, we can remove these properties.
        :param schema: json_schema in draft7
        :return: json_schema in draft7 with TOP level properties only.
        """
        streams = copy.deepcopy(catalog.model_dump())["streams"]
        for stream in streams:
            to_rem = dpath.search(
                stream["json_schema"]["properties"],
                ["**"],
                afilter=lambda x: isinstance(x, dict) and ("array" in str(x.get("type", "")) or "object" in str(x.get("type", ""))),
            )
            for key in to_rem:
                stream["json_schema"]["properties"].pop(key)
        return streams  # type: ignore  # as this comes from an AirbyteCatalog dump, the format should be fine

    def _get_relations_from_gemini(self, source_name: str, catalog: dict[str, Any]) -> Relationships:
        """

        :param source_name:
        :param catalog:
        :return: {"streams":[{'name': 'ads', 'relations': {'account_id': 'ad_account.id', 'campaign_id': 'campaigns.id', 'adset_id': 'ad_sets.id'}}, ...]}
        """
        system = "You are an Database developer in charge of communicating well to your users."

        source_desc = """
You are working on the {source_name} API service.

The current JSON Schema format is as follows:
{current_schema}, where "streams" has a list of streams, which represents database tables, and list of properties in each, which in turn, represent DB columns. Streams presented in list are the only available ones.
Generate and add a `foreign_key` with reference for each field in top level of properties that is helpful in understanding what the data represents and how are streams related to each other. Pay attention to fields ends with '_id'.
        """.format(
            source_name=source_name, current_schema=catalog
        )
        task = """
Please provide answer in the following format:
{streams: [{"name": "<stream_name>", "relations": {"<foreign_key>": "<ref_table.column_name>"} }]}
Pay extra attention that in <ref_table.column_name>" "ref_table" should be one of the list of streams, and "column_name" should be one of the property in respective reference stream.
Limitations:
- Not all tables should have relations
- Reference should point to 1 table only.
- table cannot reference on itself, on other words, e.g. `ad_account` cannot have relations with "ad_account" as a "ref_table"
        """
        response = self._model.generate_content(f"{system} {source_desc} {task}")
        md = MarkdownIt("commonmark")
        tokens = md.parse(response.text)
        response_json = json.loads(tokens[0].content)
        return response_json  # type: ignore  # we blindly assume Gemini returns a response with the Relationships format as asked

    @staticmethod
    def _get_relationships(path: Path) -> Relationships:
        if not path.exists():
            return {"streams": []}

        with open(path, "r") as file:
            return json.load(file)  # type: ignore  # we assume the content of the file matches Relationships

    def _get_catalog(self) -> AirbyteCatalog:
        with open(self._discovered_catalog_path, "r") as file:
            try:
                return AirbyteCatalog.model_validate(json.loads(file.read()))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Could not read json file {self._discovered_catalog_path}: {error}. Please ensure that it is a valid JSON."
                )

    @property
    def _erd_folder(self) -> Path:
        """
        Note: if this folder change, make sure to update the exported folder in the pipeline
        """
        path = self._source_path / "erd"
        if not path.exists():
            path.mkdir()
        return path

    @property
    def _estimated_relationships_file(self) -> Path:
        return self._erd_folder / "estimated_relationships.json"

    @property
    def _confirmed_relationships_file(self) -> Path:
        return self._erd_folder / "confirmed_relationships.json"

    @property
    def _discovered_catalog_path(self) -> Path:
        """
        Note: if this folder change, make sure to update the exported folder in the pipeline
        """
        return self._source_path / "erd" / "discovered_catalog.json"
