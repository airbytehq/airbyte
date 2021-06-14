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


from typing import Optional

from sp_api.api import Orders, Reports
from sp_api.base import Marketplaces


class AmazonClient:
    PAGECOUNT = 100

    MARKETPLACES_TO_ID = {
        "Australia": Marketplaces.AU,
        "Brazil": Marketplaces.BR,
        "Canada": Marketplaces.CA,
        "Egypt": Marketplaces.EG,
        "France": Marketplaces.FR,
        "Germany": Marketplaces.DE,
        "India": Marketplaces.IN,
        "Italy": Marketplaces.IT,
        "Japan": Marketplaces.JP,
        "Mexico": Marketplaces.MX,
        "Netherlands": Marketplaces.NL,
        "Poland": Marketplaces.PL,
        "Singapore": Marketplaces.SG,
        "Spain": Marketplaces.ES,
        "Sweden": Marketplaces.ES,
        "Turkey": Marketplaces.TR,
        "UAE": Marketplaces.AE,
        "UK": Marketplaces.UK,
        "USA": Marketplaces.US,
    }

    GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    ORDERS = "Orders"
    CURSORS = {GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL: "purchase-date", ORDERS: "LastUpdateDate"}

    _REPORT_ENTITIES = [GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL]
    _OTHER_ENTITIES = [ORDERS]
    _ENTITIES = _REPORT_ENTITIES + _OTHER_ENTITIES

    def __init__(self, credentials: dict, marketplace: str):
        self.credentials = credentials
        self.marketplace = self.MARKETPLACES_TO_ID[marketplace]

    def get_entities(self):
        return self._ENTITIES

    def is_report(self, stream_name: str) -> bool:
        if stream_name in self._REPORT_ENTITIES:
            return True
        return False

    def get_cursor_for_stream(self, stream_name: str) -> str:
        return self.CURSORS[stream_name]

    def fetch_orders(self, updated_after: str, page_size: int, next_token: Optional[str]) -> any:
        page_count = page_size or self.PAGECOUNT
        response = Orders(credentials=self.credentials, marketplace=self.marketplace).get_orders(
            LastUpdatedAfter=updated_after, MaxResultsPerPage=page_count, NextToken=next_token
        )
        return response.payload

    def request_report(self, report_type: str, data_start_time: str, data_end_time: str) -> any:
        response = Reports(credentials=self.credentials, marketplace=self.marketplace).create_report(
            reportType=report_type, dataStartTime=data_start_time, dataEndTime=data_end_time
        )

        return response.payload

    def get_report(self, report_id: str):
        response = Reports(credentials=self.credentials, marketplace=Marketplaces.IN).get_report(report_id=report_id)
        return response.payload

    def get_report_document(self, report_document_id: str):
        response = Reports(credentials=self.credentials, marketplace=Marketplaces.IN).get_report_document(report_document_id, decrypt=True)
        return response.payload
