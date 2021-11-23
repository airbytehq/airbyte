from typing import Any, Mapping
import requests

from destination_intercom.client import IntercomClient
from models import CompanyModel, ContactModel


class IntercomWriter:
    queue = []
    flush_interval = 5

    queries_per_minute = 1000

    def __init__(
        self, 
        client: IntercomClient, 
        stream: str
    ):
        self.client = client

    ## TODO: define upsert() abstract base class

    def queue_record(
        self,
        stream_name: str, 
        record_data: Mapping, 
        # written_a t: int
    ):
        self.queue.append(record_data)
        if (len(self.queue) == self.flush_interval):
            self.write_queue()

    def write_queue(self):
        for record in self.queue:
            response = self.upsert(record['user_email'])
            user_id = self.get_object_id(response)
            
            # format record and create on intercom
            airbyte_json = self.format_json_data(record)
            company_response = self.send_request(
                endpoint='companies',
                json=airbyte_json
            )
            company_id = company_response.json()["id"]
            
            # attach company to user
            response = self.send_request(
                endpoint=f'contacts/{user_id}/companies',
                json={"id": company_id}
            )
        
        self.queue.clear()

    def send_request(
        self,
        endpoint: str,
        json_payload: Mapping[str, Any]
    ):
        return self.client._request(
            http_method='post',
            endpoint=endpoint,
            json=json_payload
        )

    def get_object_id(
        self,
        upsert_response
    ):
        try:
            return html_response.json()["id"]
        except:
            return html_response.json()["data"][0]["id"]


    def format_json_data(
        self, 
        record_data: Mapping
    ):
        default_attributes = {}
        custom_attributes = {}

        for key, value in record_data.items():
            if key in self.default_attributes:
                default_attributes[key] = value
            elif key in self.excluded_attributes:
                continue
            else:
                custom_attributes[key] = value
        
        default_attributes["custom_attributes"] = custom_attributes

        return default_attributes
