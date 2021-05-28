from sp_api.api import Reports, Orders
from sp_api.base import Marketplaces


class AmazonClient:
    def __init__(self, credentials: dict):
        self.credentials = credentials
        self.marketplace = Marketplaces.IN

    def fetch_orders(self, CreatedAfter: str) -> any:
        response = Orders(credentials=self.credentials, marketplace=self.marketplace).get_orders(
            CreatedAfter=CreatedAfter)
        return response.payload

    def request_report(self, reportType: str, dataStartTime: str, dataEndTime: str) -> any:
        response = Reports(credentials=self.credentials, marketplace=self.marketplace).create_report(
            reportType=reportType, dataStartTime=dataStartTime, dataEndTime=dataEndTime)

        return response.payload

    def get_report(self, reportId: str):
        response = Reports(credentials=self.credentials,
                           marketplace=Marketplaces.IN).get_report(report_id=reportId)
        return response.payload

    def get_report_document(self, reportDocumentId: str):
        response = Reports(credentials=self.credentials, marketplace=Marketplaces.IN).get_report_document(
            reportDocumentId, decrypt=True)
        return response.payload
