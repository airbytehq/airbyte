"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import datetime
from typing import Generator

import pandas as pd
from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    Source,
    Status,
    Type,
)


class CsvSource(Source):
    """
        This source aims to provide support for readers described here:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-excel-reader

        Starting first with the read_csv primitive.
    """

    def check(self, logger, config_container) -> AirbyteConnectionStatus:
        """
            Check involves verifying that the specified csv is reachable with our credentials.
        :param logger:
        :param config_container:
        :return:
        """
        config = config_container.rendered_config
        csv_url = config["csv_url"]
        logger.info(f"Checking access to {csv_url}...")
        self.load_dataframe(config)
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger, config_container) -> AirbyteCatalog:
        config = config_container.rendered_config
        csv_url = config["csv_url"]
        logger.info(f"Discovering {csv_url}...")
        streams = []
        # TODO handle discovery of directories of csv files?
        df = self.load_dataframe(config)
        csv_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {field: {"type": self.convert_dtype(df[field].dtype)} for field in df.columns},
        }
        streams.append(AirbyteStream(name=csv_url, json_schema=csv_json_schema))
        return AirbyteCatalog(streams=streams)

    def read(self, logger, config_container, catalog_path, state_path=None) -> Generator[AirbyteMessage, None, None]:
        config = config_container.rendered_config
        csv_url = config["csv_url"]
        logger.info(f"Reading ({csv_url}, {catalog_path}, {state_path})...")
        df = self.load_dataframe(config)
        # TODO get subset of columns from catalog
        for data in df.to_dict(orient="records"):
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(stream=csv_url, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
            )

    @staticmethod
    def load_dataframe(config) -> pd.DataFrame:
        """
            From a Airbyte Configuration file, load and return the pandas dataframe
        :param config:
        :return:
        """
        csv_url = config["csv_url"]
        if "pandas.read_csv" in config:
            # pandas.read_csv additional arguments can be passed to customize how to parse csv.
            # see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            return pd.read_csv(csv_url, **config["pandas.read_csv"])
        else:
            return pd.read_csv(csv_url)

    @staticmethod
    def convert_dtype(dtype) -> str:
        """
            Convert Pandas Dataframe types to Airbyte Types
        :param dtype: Pandas Dataframe type
        :return: Corresponding Airbyte Type
        """
        if dtype == object:
            return "string"
        elif dtype in ("int64", "float64"):
            return "number"
        elif dtype == "bool":
            return "bool"
        return "string"
