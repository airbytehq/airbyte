#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import ConfigDict, BaseModel
from typing import Literal


class AvroFormat(BaseModel):
    'This connector utilises <a href="https://fastavro.readthedocs.io/en/latest/" target="_blank">fastavro</a> for Avro parsing.'
    model_config = ConfigDict(title="Avro")

    filetype: Literal["avro"] = "avro"
