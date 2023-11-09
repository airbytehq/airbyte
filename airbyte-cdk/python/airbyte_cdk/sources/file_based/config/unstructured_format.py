#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class UnstructuredFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Document File Type Format (Experimental)"
        description = "Extract text from document formats (.pdf, .docx, .md, .pptx) and emit as one record per file."
        discriminator = "filetype"

    filetype: str = Field(
        "unstructured",
        const=True,
    )
