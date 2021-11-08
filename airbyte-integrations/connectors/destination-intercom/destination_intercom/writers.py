from collections import Mapping
import requests

from destination_intercom.client import IntercomClient


class IntercomWriter:
    queue = []
    flush_interval = 1

    user_key = 'user_email'

    companies_default_attributes = [
        'name',
        'company_id'
    ]

    def __init__(self, client: IntercomClient):
        self.client = client

    def queue_record(
        self,
        stream_name: str, 
        record_data: Mapping, 
        # written_a t: int
    ):
        kv_pair = (stream_name, record_data)
        self.queue.append(kv_pair)
        if (len(self.queue) == self.flush_interval):
            self.write_queue()

    def write_queue(self):
        for stream_name, record in self.queue:
            user = record[self.user_key]
            try:
                user_response = self.client._request(
                    http_method='post',
                    endpoint='contacts',
                    json={
                        "role": "user",
                        "email": user
                    }
                )
                user_id = user_response.json()["id"]
            except requests.exceptions.HTTPError:
                user_response = self.client._request(
                    http_method='post',
                    endpoint='contacts/search',
                    json={
                        "query":  {
                            "field": "email",
                            "operator": "=",
                            "value": user
                        }
                    }
                )
                user_id = user_response.json()["data"][0]["id"]
            

            airbyte_json = self.format_json_data(record)
            company_response = self.client._request(
                http_method='post',
                endpoint='companies',
                json=airbyte_json
            )
            company_id = company_response.json()["id"]

            response = self.client._request(
                http_method='post',
                endpoint=f'contacts/{user_id}/companies',
                json={"id": company_id}
            )
        
        self.queue.clear()


    def format_json_data(self, record_data: Mapping):
        default_attributes = {}
        custom_attributes = {}

        for key, value in record_data.items():
            if key == self.user_key:
                continue
            elif key in self.companies_default_attributes:
                default_attributes[key] = value
            else:
                custom_attributes[key] = value
        
        default_attributes["custom_attributes"] = custom_attributes
        return default_attributes


class ContactWriter(IntercomWriter):
    endpoint = 'contacts'


class CompanyWriter(IntercomWriter):
    endpoint = 'companies'
