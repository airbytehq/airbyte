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

from typing import List, Optional

from pydantic import BaseModel, Field

config_path: str = Field(description="Path to a JSON object representing a valid connector configuration")
invalid_config_path: str = Field(description="Path to a JSON object representing an invalid connector configuration")
spec_path: str = Field(description="Path to a JSON object representing the spec expected to be output by this connector")
configured_catalog_path: str = Field(description="Path to configured catalog")


class SpecTestConfig(BaseModel):
    class Config:
        extra = "forbid"

    spec_path: str = spec_path


class ConnectionTestConfig(BaseModel):
    class Config:
        extra = "forbid"

    config_path: str = config_path
    invalid_config_path: str = invalid_config_path


class DiscoveryTestConfig(BaseModel):
    class Config:
        extra = "forbid"

    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path


class BasicReadTestConfig(BaseModel):
    class Config:
        extra = "forbid"

    config_path: str = config_path
    configured_catalog_path: Optional[str] = configured_catalog_path
    validate_output_from_all_streams: bool = Field(False, description="Verify that all streams have records")


class FullRefreshConfig(BaseModel):
    class Config:
        extra = "forbid"

    config_path: str = config_path
    configured_catalog_path: str = configured_catalog_path


class IncrementalConfig(BaseModel):
    class Config:
        extra = "forbid"

    config_path: str = config_path
    configured_catalog_path: str = configured_catalog_path


class TestConfig(BaseModel):
    class Config:
        extra = "forbid"

    spec: Optional[List[SpecTestConfig]] = Field(description="TODO")
    connection: Optional[List[ConnectionTestConfig]] = Field(description="TODO")
    discovery: Optional[List[DiscoveryTestConfig]] = Field(description="TODO")
    basic_read: Optional[List[BasicReadTestConfig]] = Field(description="TODO")
    full_refresh: Optional[List[FullRefreshConfig]] = Field(description="TODO")
    incremental: Optional[List[IncrementalConfig]] = Field(description="TODO")


class Config(BaseModel):
    class Config:
        extra = "forbid"

    connector_image: str = Field(description="Docker image to test, for example 'airbyte/source-hubspot:dev'")
    base_path: Optional[str] = Field(description="Base path for all relative paths")
    tests: TestConfig = Field(description="TODO")
