#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import json
import uuid
from typing import List, Generator, Dict

from hdfs import InsecureClient


class HDFSClient:
    def __init__(
        self,
        host: str,
        user: str,
        destination_path: str,
        stream: str,
        overwrite: bool = False,
        port: int = 50070,
        logger=None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.destination_path = destination_path
        self.stream = stream
        self.overwrite = overwrite
        self.logger = logger

    def get_client(self) -> InsecureClient:
        return InsecureClient(f"http://{self.host}:{self.port}", user=self.user)

    @property
    def path(self) -> str:
        return f"{self.destination_path}/airbyte_json_{self.stream}.jsonl"

    def write(self, data: Generator[str, None, None], overwrite: bool = False) -> None:
        _client = self.get_client()
        path = self.path
        _client.makedirs(self.destination_path)
        self.logger.info(f"Overwrite: {overwrite}")
        # HDFS does not handle the overwrite/append situation gracefully, so
        # we need to add some preliminary steps before writing
        exists = _client.status(path, strict=False)
        if overwrite and exists:
            # Delete the file before writing
            _client.delete(path)
            exists = False
        if not exists:
            # Create an empty file for writing
            _client.write(path, encoding="utf-8", data="")
        _client.write(path, encoding="utf-8", data=data, append=True)

    def check(self) -> None:
        filename = f"{self.destination_path}/_airbyte_test_{uuid.uuid4()}.txt"
        _client = self.get_client()
        _client.write(filename, data="", encoding="utf-8")
        _client.delete(filename)

    def read_data(self) -> List[Dict]:
        _client = self.get_client()
        with _client.read(self.path, encoding="utf-8") as reader:
            data = reader.read()
        return [json.loads(line) for line in data.split("\n")]
