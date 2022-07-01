#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import dpath.util
import pytest
from airbyte_cdk.sources.streams.files import FilesSpec
from pydantic import BaseModel, Field

logger = logging.getLogger("airbyte")


class MockBrokenSpec(FilesSpec, BaseModel):
    class Config:
        title = "Mock Spec"


class MockSpec(FilesSpec, BaseModel):
    class Config:
        title = "Mock Spec"

    class MockProvider(BaseModel):
        class Config:
            title = "Mock Provider"

    provider: MockProvider = Field(...)


class TestFilesSpec:
    def test_post_processing_no_provider(self):
        with pytest.raises(RuntimeError):
            MockBrokenSpec.schema()

    def test_post_processing(self):
        out_schema = MockSpec.schema()
        assert len([x for x in dpath.util.search(out_schema, "**/anyOf")]) == 0
        assert len([x for x in dpath.util.search(out_schema, "**/oneOf")]) > 0
        assert len([x for x in dpath.util.search(out_schema, "**/$ref")]) == 0

    def test_without_post_processing(self):
        # we should prove that the above assertions would NOT hold without the added post-processing

        delattr(FilesSpec, "schema")  # this removes our method override

        # and now we create a class based on FilesSpec without the schema() override
        class MockSpecWithoutPostProcessing(FilesSpec, BaseModel):
            class Config:
                title = "Mock Spec"

            class MockProvider(BaseModel):
                class Config:
                    title = "Mock Provider"

            provider: MockProvider = Field(...)

        out_schema = MockSpecWithoutPostProcessing.schema()
        assert len([x for x in dpath.util.search(out_schema, "**/anyOf")]) > 0
        assert len([x for x in dpath.util.search(out_schema, "**/oneOf")]) == 0
        assert len([x for x in dpath.util.search(out_schema, "**/$ref")]) > 0
