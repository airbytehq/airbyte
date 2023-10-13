#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class UnstructuredFormat(BaseModel):
    class Config:
        title = "Markdown/PDF/Docx Format (Experimental)"
        schema_extra = {"description": "Extract text from document formats and emit as one record per file."}

    filetype: str = Field(
        "unstructured",
        const=True,
    )
