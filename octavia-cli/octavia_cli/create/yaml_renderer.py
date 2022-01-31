from attr import attr
from .definition_specification import DefinitionSpecification

from pathlib import Path
from tempfile import TemporaryDirectory

from datamodel_code_generator import InputFileType, generate
import importlib.util
import inspect
from pydantic_factories import ModelFactory

from octavia_cli.create import schema_utils

class Field:

    def __init__(self, name, type, is_required, description, examples) -> None:
        self.name = name
        self.type = type
        self.is_required = is_required
        self.description = description
        self.examples = examples

class Renderer:

    def __init__(self, definition_specification: DefinitionSpecification) -> None:
        self.definition_specification = definition_specification
        self.pydantic_model = self._get_pydantic_model()
        self.schema_properties = self.pydantic_model.schema(by_alias=True).get(
            "properties", {}
        )
        self.schema_references = self.pydantic_model.schema(by_alias=True).get(
            "definitions", {}
        )
        self.required_properties = self.pydantic_model.schema(by_alias=True).get(
            "required", []
        )
    @staticmethod
    def patch_generated_model(model_path):
            with open(model_path, "r") as fp:
                lines = fp.readlines()
            with open(model_path, "w") as fp:
                for line in lines:
                    if line.strip("\n") != "from __future__ import annotations":
                        fp.write(line)
    
    def _get_pydantic_model(self):
        #TODO make sure its deleted
        with TemporaryDirectory() as temporary_directory_name:
            temporary_directory = Path(temporary_directory_name)
            output = Path(temporary_directory / f'{self.definition_specification.id}.py')
            generate(
                self.definition_specification.json_schema,
                input_file_type=InputFileType.JsonSchema,
                input_filename=f"{self.definition_specification.id}.json",
                output=output,
            )
            generate(
                self.definition_specification.json_schema,
                input_file_type=InputFileType.JsonSchema,
                input_filename=f"{self.definition_specification.id}.json",
                output=Path("/users/augustin/Desktop/output.py"),
            )
            self.patch_generated_model(output)
            spec = importlib.util.spec_from_file_location(self.definition_specification.id, output)
            pydantic_models = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(pydantic_models)
            for member_name, obj in inspect.getmembers(pydantic_models):
                try:
                    print(obj.__fields__)
                except AttributeError:
                    continue
            spec_class = [obj for member_name, obj in inspect.getmembers(pydantic_models) if member_name.endswith("Spec")][0]
        return spec_class

    def render(self):
        fields = []
        for name, field in self.pydantic_model.__fields__.items():
            print(f"{field.name}: {field.default} # {field._type_display()} - {'REQUIRED' if field.required else ''}")