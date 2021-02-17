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

import os

from base_python import AirbyteLogger
from base_singer import ConfigContainer
from source_github_singer import SourceGithubSinger

logger = AirbyteLogger()


class TestSourceGithub(object):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    private_repo_config_path: str = os.path.join(base_dir, "secrets/private_config.json")
    private_repo_catalog_path: str = os.path.join(base_dir, "resourcesstandardtest/private_configured_catalog.json")

    def test_private_repo(self):
        singer = SourceGithubSinger()
        config = singer.read_config(self.private_repo_config_path)
        configure_container = ConfigContainer(config, self.private_repo_config_path)
        generator = singer.read(logger, configure_container, self.private_repo_catalog_path)
        for message in generator:
            print(message.json(exclude_unset=True))
