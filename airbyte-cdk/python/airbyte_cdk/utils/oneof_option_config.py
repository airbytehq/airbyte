#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Optional

from pydantic import ConfigDict


def handle_one_of(schema: Dict[str, Any], model: Any) -> None:
    if model.model_config.get("description"):
        schema["description"] = model.model_config["description"]
    if model.model_config.get("discriminator"):
        schema.setdefault("required", []).append(model.model_config["discriminator"])


def one_of_model_config(title: Optional[str] = None, description: Optional[str] = None, discriminator: Optional[str] = None) -> ConfigDict:
    return ConfigDict(json_schema_extra=handle_one_of, **{"title": title, "description": description, "discriminator": discriminator})
