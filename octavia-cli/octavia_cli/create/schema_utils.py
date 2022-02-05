#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


def parse_properties(required_fields, properties):
    return [Field(f_name, f_name in required_fields, f_metadata) for f_name, f_metadata in properties.items()]


def get_object_properties(field_metadata):
    if field_metadata.get("properties"):
        required_fields = field_metadata.get("required", [])
        return parse_properties(required_fields, field_metadata["properties"])
    return []


class Field:
    def __init__(self, name, required, field_metadata):
        self.name = name
        self.required = required
        self.field_metadata = field_metadata
        self.one_of_values = self.get_one_of_values()
        self.object_properties = get_object_properties(field_metadata)
        self.array_items = self.get_array_items()
        self.comment = self.build_comment(
            [
                self.get_secret_comment,
                self.get_required_comment,
                self.get_type_comment,
                self.get_description_comment,
                self.get_example_comment,
            ]
        )

    def __getattr__(self, name: str):
        """Map field_metadata keys to attributes of Field"""
        if name in self.field_metadata:
            return self.field_metadata.get(name)

    @property
    def is_array_of_objects(self):
        if self.type == "array" and self.items:
            if self.items["type"] == "object":
                return True
        return False

    def get_one_of_values(self):
        if not self.oneOf:
            return []
        one_of_values = []
        for one_of_value in self.oneOf:
            properties = get_object_properties(one_of_value)
            one_of_values.append(properties)
        return one_of_values

    def get_array_items(self):
        if self.is_array_of_objects:
            required_fields = self.items.get("required", [])
            return parse_properties(required_fields, self.items["properties"])
        return []

    def get_required_comment(self):
        return "REQUIRED" if self.required else "OPTIONAL"

    def get_type_comment(self):
        return str(self.type) if self.type else None

    def get_secret_comment(self):
        return "🤫" if self.airbyte_secret else None

    def get_description_comment(self):
        return self.description if self.description else None

    def get_example_comment(self):
        example_comment = None
        if self.examples:
            if isinstance(self.examples, list):
                if len(self.examples) > 1:
                    example_comment = f"Examples: {', '.join([str(example) for example in self.examples])}"
                else:
                    example_comment = f"Example: {self.examples[0]}"
            else:
                example_comment = f"Example: {self.examples}"
        return example_comment

    @property
    def default_value(self):
        """[summary]
        Default values are the only YAML values wrote to the yaml file.
        We need to make sure they are safe for valid yaml parsing.
        Returns:
            [type]: [description]
        """
        if self.const:
            return self.const
        return self.default

    @staticmethod
    def build_comment(comment_functions):
        return " | ".join(filter(None, [comment_fn() for comment_fn in comment_functions])).replace("\n", "")
