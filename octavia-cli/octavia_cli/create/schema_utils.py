#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


def parse_properties(required_fields, properties):
    return [Field(f_name, f_name in required_fields, f_metadata) for f_name, f_metadata in properties.items()]


class Field:
    def __init__(self, name, required, field_metadata):
        self.name = name
        self.required = required
        self.field_metadata = field_metadata
        self.title = field_metadata.get("title")
        self.type_hint = field_metadata.get("type")
        self.description = field_metadata.get("description")
        self.examples = field_metadata.get("examples", [])
        self.default = field_metadata.get("default")
        self.const = field_metadata.get("const")
        self.is_secret = field_metadata.get("airbyte_secret", False)
        self.is_one_of = "oneOf" in self.field_metadata
        self.is_array_of_objects = (
            self.type_hint == "array" and "items" in self.field_metadata and self.field_metadata["items"]["type"] == "object"
        )
        self.is_object = self.type_hint == "object"
        self.one_of_values = self.get_one_of_values()
        self.object_properties = self.get_object_properties(field_metadata)
        self.array_items = self.get_array_items()

    def get_one_of_values(self):
        if not self.is_one_of:
            return []
        one_of_values = []
        for one_of_value in self.field_metadata.get("oneOf"):
            properties = self.get_object_properties(one_of_value)
            one_of_values.append(properties)
        return one_of_values

    @staticmethod
    def get_object_properties(field_metadata):
        if field_metadata.get("properties"):
            required_fields = field_metadata.get("required", [])
            return parse_properties(required_fields, field_metadata["properties"])
        return []

    def get_array_items(self):
        if self.is_array_of_objects:
            required_fields = self.field_metadata["items"].get("required", [])
            return parse_properties(required_fields, self.field_metadata["items"]["properties"])
        return []

    @property
    def comment(self):
        comment_items = []
        if self.is_secret:
            comment_items.append("🤫")
        comment_items.append("REQUIRED" if self.required else "OPTIONAL")
        comment_items.append(f"Type: {self.type_hint}")
        if self.description:
            comment_items.append(self.description)
        if self.examples:
            if isinstance(self.examples, list):
                comment_items.append(f"Examples: {', '.join([str(example) for example in self.examples])}")
            else:
                comment_items.append(f"Example: {self.examples}")
        return " | ".join(comment_items).replace("\n", "")

    @property
    def default_value(self):
        """[summary]
        Default values are the only YAML values wrote to the yaml file.
        We need to make sure they are safe for valid yaml parsing.
        Returns:
            [type]: [description]
        """
        default = ""
        if self.const:
            default = self.const
        if self.default is not None:
            default = self.default
        if default == '"':
            default = "'\"'"
        elif default == "'":
            default = '"\'"'
        elif isinstance(default, str):
            if '"' not in default:
                default = f'"{default}"'
            else:
                default = f"'{default}'"
        return default

    def __repr__(self) -> str:
        return self.name
