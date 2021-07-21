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
from pathlib import Path
from typing import TextIO, Optional, Dict

import paramiko
import smart_open


class SftpClient:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        destination_path: str,
        filename: str = "data",
        port: int = 22,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.file_path = Path(destination_path) / f"{filename}.jsonl"
        self._file: Optional[TextIO] = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_uri(self) -> str:
        return f"sftp://{self.username}:{self.password}@{self.host}:{self.port}/{self.file_path}"

    def _open(self) -> TextIO:
        # Explicitly turn off ssh keys stored in ~/.ssh
        transport_params = {"connect_kwargs": {"look_for_keys": False}}

        uri = self._get_uri()
        return smart_open.open(uri, transport_params=transport_params, mode="w+")

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def open(self):
        self.close()
        self._file = self._open()
        return self

    def write(self, record: Dict) -> None:
        if self._file is None:
            self.open()
        text = json.dumps(record)
        self._file.write(f"{text}\n")

    def delete(self) -> None:
        with paramiko.SSHClient() as client:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                self.host,
                self.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
            )
            sftp = client.open_sftp()
            sftp.remove(str(self.file_path))
