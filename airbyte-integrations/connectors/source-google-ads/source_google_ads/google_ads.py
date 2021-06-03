from google.ads.googleads.client import GoogleAdsClient
from typing import Any, Tuple, Mapping, List
from string import Template

REPORT_MAPPING = {
    "ad_performance_report": "ad_group_ad"
}


class GoogleAds:
    DEFAULT_PAGE_SIZE = 10

    def __init__(self, credentials: Tuple[str, Any], customer_id: str):
        self.client = GoogleAdsClient.load_from_dict(credentials)
        self.customer_id = customer_id
        self.ga_service = self.client.get_service("GoogleAdsService")

    def send_request(self, query: str, page_token: str):
        client = self.client
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = self.customer_id
        search_request.query = query
        search_request.page_size = self.DEFAULT_PAGE_SIZE
        if page_token:
            search_request.page_token = page_token
        return self.ga_service.search(search_request)

    @staticmethod
    def Create(developer_token: str, refresh_token: str, client_id: str, client_secret: str, customer_id: str, **kwargs):

        credentials = {
            "developer_token": developer_token,
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret}

        return GoogleAds(credentials, customer_id)

    @staticmethod
    def get_fields_from_schema(schema: Mapping[str, Any]) -> List[str]:
        properties = schema.get('json_schema').get('properties')
        return [properties.get(key).get("field")
                for key in properties.keys()]

    @staticmethod
    def convert_schema_into_query(schema: Mapping[str, Any], report_name: str, from_date: str, to_date: str) -> str:
        from_category = REPORT_MAPPING[report_name]
        fields = GoogleAds.get_fields_from_schema(schema)
        fields = ",\n".join(fields)

        query = Template("""
          SELECT
            $fields
          FROM $from_category
          WHERE segments.date > '$from_date'
          AND segments.date < '$to_date'
      """)
        query = query.substitute(
            fields=fields, from_category=from_category, from_date=from_date, to_date=to_date)
        return query

    @staticmethod
    def get_field_value(result, field) -> str:
        field_name = field.split(".")
        try:
            field_value = result
            for level_attr in field_name:
                field_value = field_value.__getattr__(level_attr)
            field_value = str(field_value)
        except:
            field_value = None

        return field_value

    @staticmethod
    def parse_single_result(schema: Mapping[str, Any], result):
        properties = schema.get('json_schema').get('properties')
        fields = [{"name": key, "field_path": properties.get(key).get("field")}
                  for key in properties.keys()]
        single_record = {}
        for field in fields:
            single_record[field["name"]] = GoogleAds.get_field_value(
                result, field["field_path"])
        return single_record
