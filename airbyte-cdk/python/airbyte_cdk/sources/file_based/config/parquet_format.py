from pydantic import BaseModel, Field
from typing_extensions import Literal


class ParquetFormat(BaseModel):
    filetype: Literal["parquet"] = "parquet"
    decimal_as_float: bool = Field(
        title="Convert Decimal Fields to Floats",
        description="Whether to convert decimal fields to floats. This is the legacy behavior of the S3 source."
                    "There is a loss of precision when converting decimals to floats, so this is not recommended.",
        default=False,
    )
