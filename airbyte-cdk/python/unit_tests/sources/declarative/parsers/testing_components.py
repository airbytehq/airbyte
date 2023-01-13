#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import List, Optional

from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.paginators import PaginationStrategy
from airbyte_cdk.sources.declarative.stream_slicers import SubstreamSlicer


@dataclass
class TestingSomeComponent(DefaultErrorHandler):
    """
    A basic test class with various field permutations used to test manifests with custom components
    """

    subcomponent_field_with_hint: DpathExtractor = DpathExtractor(field_pointer=[], config={}, options={})
    basic_field: str = ""
    optional_subcomponent_field: Optional[RequestOption] = None
    list_of_subcomponents: List[RequestOption] = None
    without_hint = None


@dataclass
class TestingCustomSubstreamSlicer(SubstreamSlicer):
    """
    A test class based on a SubstreamSlicer used for testing manifests that use custom components.
    """

    custom_field: str
    custom_pagination_strategy: PaginationStrategy
