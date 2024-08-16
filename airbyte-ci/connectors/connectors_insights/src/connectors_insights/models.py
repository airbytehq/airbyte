# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime

from connector_ops.utils import ConnectorLanguage  # type: ignore
from pydantic import BaseModel, StrictBool
from pydantic.json import pydantic_encoder


class ConnectorInsights(BaseModel):
    insight_generation_timestamp: datetime
    connector_definition_id: str
    connector_type: str
    connector_subtype: str | None
    connector_technical_name: str
    connector_version: str
    connector_image_address: str
    connector_support_level: str | None
    ab_internal_sl: int | None
    ab_internal_ql: int | None
    cdk_name: str | None
    cdk_version: str | None
    connector_language: ConnectorLanguage | None
    ci_on_master_report: dict | None
    ci_on_master_passes: StrictBool | None
    uses_base_image: StrictBool
    base_image_address: str | None
    base_image_version: str | None
    is_using_poetry: StrictBool
    dependencies: list[dict]
    is_cloud_enabled: StrictBool
    is_oss_enabled: StrictBool
    deprecated_classes_in_use: list[str] | None
    deprecated_modules_in_use: list[str] | None
    forbidden_method_names_in_use: list[str] | None
    manifest_uses_parameters: StrictBool | None
    manifest_uses_custom_components: StrictBool | None
    manifest_custom_component_classes: list[str] | None
    has_json_schemas: StrictBool | None

    class Config:
        json_encoders = {dict: lambda v: json.dumps(v, default=pydantic_encoder)}
