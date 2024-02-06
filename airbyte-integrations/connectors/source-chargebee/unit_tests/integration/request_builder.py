# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import List, Optional

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS

class ChargebeeRequestBuilder:

  @classmethod
  def addon_endpoint(cls, site: str, api_key: str) -> "ChargebeeRequestBuilder":
      return cls("addon", site, api_key)

  @classmethod
  def plan_endpoint(cls, site: str, api_key: str) -> "ChargebeeRequestBuilder":
      return cls("plan", site, api_key)

  @classmethod
  def virtual_bank_account_endpoint(cls, site: str, api_key: str) -> "ChargebeeRequestBuilder":
      return cls("virtual_bank_account", site, api_key)

  @classmethod
  def event_endpoint(cls, site: str, api_key: str) -> "ChargebeeRequestBuilder":
      return cls("event", site, api_key)

  @classmethod
  def site_migration_detail_endpoint(cls, site: str, api_key: str) -> "ChargebeeRequestBuilder":
      return cls("site_migration_detail", site, api_key)

  # TBD if needed
  @classmethod
  def hosted_page_endpoint(cls, site: str, api_key: str) -> "ChargebeeRequestBuilder":
      return cls("hosted_page", site, api_key)