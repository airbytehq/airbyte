#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Literal, Optional, Union

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class LocalProcessingConfigModel(BaseModel):
    mode: Literal["local"] = Field("local", const=True)

    class Config(OneOfOptionConfig):
        title = "Local"
        description = "Process files locally, supporting `fast` and `ocr` modes. This is the default option."
        discriminator = "mode"


class APIParameterConfigModel(BaseModel):
    name: str = Field(
        title="Parameter name",
        description="The name of the unstructured API parameter to use",
        examples=["include_page_breaks", "strategy"],
    )
    value: str = Field(title="Value", description="The value of the parameter", examples=["true", "hi_res"])


class APIProcessingConfigModel(BaseModel):
    mode: Literal["api"] = Field("api", const=True)

    api_key: str = Field(
        default="",
        always_show=True,
        title="API Key",
        airbyte_secret=True,
        description="The API key to use matching the environment",
    )

    api_url: str = Field(
        default="https://api.unstructured.io",
        title="API URL",
        always_show=True,
        description="The URL of the unstructured API to use",
        examples=["https://api.unstructured.com"],
    )

    parameters: Optional[List[APIParameterConfigModel]] = Field(
        default=[],
        always_show=True,
        title="Parameters",
        description="List of parameters send to the API",
    )

    class Config(OneOfOptionConfig):
        title = "via API"
        description = "Process files via an API, using the `hi_res` mode. This option is useful for increased performance and accuracy, but requires an API key and a hosted instance of unstructured."
        discriminator = "mode"


class UnstructuredFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Document File Type Format (Experimental)"
        description = "Extract text from document formats (.pdf, .docx, .md, .pptx) and emit as one record per file."
        discriminator = "filetype"

    filetype: str = Field(
        "unstructured",
        const=True,
    )

    skip_unprocessable_file_types: bool = Field(
        default=True,
        title="Skip Unprocessable File Types",
        description="If true, skip files that cannot be parsed because of their file type and log a warning. If false, fail the sync. Corrupted files with valid file types will still result in a failed sync.",
        always_show=True,
    )

    processing: Union[LocalProcessingConfigModel, APIProcessingConfigModel,] = Field(
        default=LocalProcessingConfigModel(mode="local"),
        title="Processing",
        description="Processing configuration",
        discriminator="mode",
        type="object",
    )
