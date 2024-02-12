#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict


class OneOfOptionConfig:
    """
    Base class to configure a Pydantic model that's used as a oneOf option in a parent model in a way that's compatible with all Airbyte consumers.

    Inherit from this class in the nested Config class in a model and set title and description (these show up in the UI) and discriminator (this is making sure it's marked as required in the schema).

    Usage:

        ```python
        class OptionModel(BaseModel):
            mode: Literal["option_a"] = Field("option_a", const=True)
            option_a_field: str = Field(...)

            class Config(OneOfOptionConfig):
                title = "Option A"
                description = "Option A description"
                discriminator = "mode"
        ```
    """

    @staticmethod
    def schema_extra(schema: Dict[str, Any], model: Any) -> None:
        if hasattr(model.Config, "description"):
            schema["description"] = model.Config.description
        if hasattr(model.Config, "discriminator"):
            schema.setdefault("required", []).append(model.Config.discriminator)
