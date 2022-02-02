#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import importlib.util
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import datamodel_code_generator
import tomlkit
from pydantic.typing import get_origin, is_union

from .definition_specification import DefinitionSpecification


class Renderer:
    def __init__(self, definition_specification: DefinitionSpecification) -> None:
        self.definition_specification = definition_specification
        self.pydantic_model = self._get_pydantic_model()

    @staticmethod
    def _patch_generated_model(model_path):
        # TODO alafanechere explain why
        with open(model_path, "r") as fp:
            lines = fp.readlines()
        with open(model_path, "w") as fp:
            for line in lines:
                if line.strip("\n") != "from __future__ import annotations":
                    fp.write(line)

    def _get_pydantic_model(self):
        # TODO alafanechere make sure tempdir is deleted
        with TemporaryDirectory() as temporary_directory_name:
            temporary_directory = Path(temporary_directory_name)
            output = Path(temporary_directory / f"{self.definition_specification.id}.py")
            datamodel_code_generator.generate(
                self.definition_specification.json_schema,
                input_file_type=datamodel_code_generator.InputFileType.JsonSchema,
                input_filename=f"{self.definition_specification.id}.json",
                output=output,
            )
            self._patch_generated_model(output)
            spec = importlib.util.spec_from_file_location(self.definition_specification.id, output)
            pydantic_models = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(pydantic_models)
            for member_name, obj in inspect.getmembers(pydantic_models):
                # TODO alafanechere do we have a more
                if member_name.endswith("Spec"):
                    return obj
            raise Exception("Could not find main spec class")

    @staticmethod
    def build_comment(field):
        comments = []
        if field.field_info.title:
            comments.append(field.field_info.title)
        comments.append(f"Type: {field._type_display()}")
        if field.field_info.description:
            comments.append(field.field_info.description)
        if field.field_info.extra.get("examples"):
            comments.append(f"Examples: {field.field_info.extra['examples']}")
        return " | ".join(comments).replace("\n", "")  # remove new lines because they are not commented by tomlkit

    @staticmethod
    def get_default_value(field):
        default_value = ""
        if field.default is None and field.field_info.extra.get("examples"):
            default_value = field.field_info.extra["examples"][0]
        if isinstance(field.default, bool):
            default_value = str(field.default)
        return default_value

    def render(self, section, fields):
        for field in fields:
            if field.sub_fields and is_union(get_origin(field.type_)):
                for i, sub_field in enumerate(field.sub_fields):
                    new_section = tomlkit.table()
                    rendered_section = self.render(new_section, sub_field.type_.__fields__.values())
                    if i == 0:
                        section.add(f"{field.name}", rendered_section)
                    else:
                        if i == 1:
                            section.add(tomlkit.comment(f"{field.name} has multiple valid structures, you'll find examples below:"))
                            section.add(tomlkit.nl())
                        section.add(tomlkit.comment(f"Another {field.name}"))
                        for commented_line in tomlkit.dumps(rendered_section).split("\n"):
                            if commented_line:
                                section.add(tomlkit.comment(commented_line))
                    section.add(tomlkit.nl())
            else:
                section.add(field.name, self.get_default_value(field))
                section[field.name].value.comment(self.build_comment(field))
        return section

    def build_file_header(self, document):
        header_comments = [
            f"Configuration for {self.definition_specification.definition.docker_repository}",
            f"Documentation about this connector can be found at {self.definition_specification.documentation_url}",
        ]
        for header_comment in header_comments:
            document.add(tomlkit.comment(header_comment))
        document.add("definition_id", self.definition_specification.id)
        document.add("definition_image", self.definition_specification.definition.docker_repository)
        document.add("definition_version", self.definition_specification.definition.docker_image_tag)

        document.add(tomlkit.nl())
        document.add(tomlkit.comment("EDIT THE CONFIGURATION BELOW"))
        return document

    def write_toml(self, toml_file_path):
        document = tomlkit.document()
        document = self.build_file_header(document)

        configuration_section = tomlkit.table(is_super_table=True)
        document["configuration"] = self.render(configuration_section, self.pydantic_model.__fields__.values())
        with open(toml_file_path, "w") as f:
            tomlkit.dump(document, f)
        return toml_file_path
