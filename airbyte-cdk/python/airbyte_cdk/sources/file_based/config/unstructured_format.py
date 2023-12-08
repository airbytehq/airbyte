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

    skip_unprocessable_files: Optional[bool] = Field(
        default=True,
        title="Skip Unprocessable Files",
        description="If true, skip files that cannot be parsed and pass the error message along as the _ab_source_file_parse_error field. If false, fail the sync.",
        always_show=True,
    )
