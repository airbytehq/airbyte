#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

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

    skip_unprocessable_file_types: Optional[bool] = Field(
        default=True,
        title="Skip Unprocessable File Types",
        description="If true, skip files that cannot be parsed because of their file type and log a warning. If false, fail the sync. Corrupted files with valid file types will still result in a failed sync.",
        always_show=True,
    )
