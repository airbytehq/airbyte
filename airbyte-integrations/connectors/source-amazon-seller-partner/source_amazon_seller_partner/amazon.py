from sp_api.api import Reports, Orders
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
        "USA": Marketplaces.US
    }

    GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    ORDERS = "Orders"
    CURSORS = {
        GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL: "last-updated-date",
        ORDERS: "LastUpdatedAfter"
    }

    _REPORT_ENTITIES = [GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL]
    _OTHER_ENTITIES = [ORDERS]
    _ENTITIES = _REPORT_ENTITIES + _OTHER_ENTITIES

    def __init__(self, credentials: dict, marketplace: str):
        self.credentials = credentials
        self.marketplace = self.MARKETPLACES_TO_ID[marketplace]

    def get_entities(self):
        return self._ENTITIES

    def fetch_entity_for_stream(self, stream_name: str) -> str:
        if stream_name in self._REPORT_ENTITIES:
            return "report"
        else:
            return "other"

    def get_cursor_for_stream(self, stream_name: str) -> str:
        return self.CURSORS[stream_name]

    def fetch_orders(self, updated_after: str, page_size: int, next_token: str) -> any:
        page_count = page_size or self.PAGECOUNT
        response = Orders(credentials=self.credentials, marketplace=self.marketplace).get_orders(
            LastUpdatedAfter=updated_after, MaxResultsPerPage=page_count, NextToken=next_token)
        return response.payload

    def request_report(self, report_type: str, data_start_time: str, data_end_time: str) -> any:
        response = Reports(credentials=self.credentials, marketplace=self.marketplace).create_report(
            reportType=report_type, dataStartTime=data_start_time, dataEndTime=data_end_time)

        return response.payload

    def get_report(self, report_id: str):
        response = Reports(credentials=self.credentials,
                           marketplace=Marketplaces.IN).get_report(report_id=report_id)
        return response.payload

    def get_report_document(self, report_document_id: str):
        response = Reports(credentials=self.credentials, marketplace=Marketplaces.IN).get_report_document(
            report_document_id, decrypt=True)
        return response.payload
