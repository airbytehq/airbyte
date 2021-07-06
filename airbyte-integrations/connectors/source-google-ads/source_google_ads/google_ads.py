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

from enum import Enum
from string import Template
from typing import Any, List, Mapping

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v7.services.types.google_ads_service import GoogleAdsRow, SearchGoogleAdsResponse

REPORT_MAPPING = {"ad_group_ad_report": "ad_group_ad"}


class GoogleAds:
    DEFAULT_PAGE_SIZE = 1000

    def __init__(self, credentials: Mapping[str, Any], customer_id: str):
        self.client = GoogleAdsClient.load_from_dict(credentials)
        self.customer_id = customer_id
        self.ga_service = self.client.get_service("GoogleAdsService")

    def send_request(self, query: str) -> SearchGoogleAdsResponse:
        client = self.client
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = self.customer_id
        search_request.query = query
        search_request.page_size = self.DEFAULT_PAGE_SIZE

        return self.ga_service.search(search_request)

    @staticmethod
    def get_fields_from_schema(schema: Mapping[str, Any]) -> List[str]:
        properties = schema.get("properties")

        return [*properties]

    @staticmethod
    def convert_schema_into_query(schema: Mapping[str, Any], report_name: str, from_date: str, to_date: str) -> str:
        from_category = REPORT_MAPPING[report_name]
        fields = GoogleAds.get_fields_from_schema(schema)
        fields = ",\n".join(fields)

        query = Template(
            """
          SELECT
            $fields
          FROM $from_category
          WHERE segments.date > '$from_date'
            AND segments.date < '$to_date'
          ORDER BY segments.date
      """
        )
        query = query.substitute(fields=fields, from_category=from_category, from_date=from_date, to_date=to_date)

        return query

    @staticmethod
    def get_field_value(result: GoogleAdsRow, field: str) -> str:
        field_name = field.split(".")
        try:
            field_value = result
            for level_attr in field_name:
                field_value = field_value.__getattr__(level_attr)
                if isinstance(field_value, Enum):
                    field_value = field_value.name
            field_value = str(field_value)
        except Exception:
            field_value = None

        return field_value

    @staticmethod
    def parse_single_result(schema: Mapping[str, Any], result: GoogleAdsRow):
        fields = GoogleAds.get_fields_from_schema(schema)
        single_record = {}
        for field in fields:
            single_record[field] = GoogleAds.get_field_value(result, field)
        return single_record
