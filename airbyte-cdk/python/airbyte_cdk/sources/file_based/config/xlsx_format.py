#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class XlsxFormat(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Xlsx Format"
        discriminator = "filetype"

    filetype: str = Field(
        "xlsx",
        const=True,
    )
    sheet_name: str = Field(
        title="Sheet Name or Index",
        description="The name or index of the sheet that will be read from the workbook into the stream.",
    )
