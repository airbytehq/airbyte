from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import requests
from .streams import Views, Sessions, YandexMetricaStream
from .fields import HitsFields, VisitsFields

# Source
class SourceYandexMetrica(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            hits_all_fields = HitsFields.get_all_fields_names_list()
            hits_required_fields = HitsFields.get_required_fields_names_list()
            visits_all_fields = VisitsFields.get_all_fields_names_list()
            visits_required_fields = VisitsFields.get_required_fields_names_list()
            # Check fields are valid
            for field in config['hits_fields']:
                if field not in hits_all_fields:
                    return False, f'Fields from "hits" cannot contrain "{field}"' 
            for field in config['visits_fields']:
                if field not in visits_all_fields:
                    return False, f'Fields from "visits" cannot contrain "{field}"' 

            # Check if required fields are presest
            if not all(x in config['hits_fields'] for x in hits_required_fields):
                return False, f'Fields from "hits" must contain "{", ".join(hits_required_fields)}"' 
            if not all(x in config['visits_fields'] for x in visits_required_fields):
                return False, f'Fields from "visits" must contain "{", ".join(visits_required_fields)}"' 

            # Check connectivity
            counter_id = config['counter_id']
            authenticator = TokenAuthenticator(token=config["auth_token"])
            # Check Views stream
            views_params = {
                'source': 'hits',
                'fields': config['hits_fields'],
                'start_date': config['start_date'],
                'end_date': config['end_date']
            }
            views_ok, views_error = self.evaluate(authenticator, counter_id, views_params)
            if not views_ok:
                raise Exception(f"Views stream connection check failed. Error: {views_error}")
            # Check Sessions stream
            sessions_params = {
                'source': 'visits',
                'fields': config['visits_fields'],
                'start_date': config['start_date'],
                'end_date': config['end_date']
            }
            sessions_ok, sessions_error = self.evaluate(authenticator, counter_id, sessions_params)
            if not sessions_ok:
                raise Exception(f"Sessions stream connection check failed. Error: {sessions_error}")

            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[YandexMetricaStream]:
        authenticator = TokenAuthenticator(token=config["auth_token"])
        views_stream_args = {
            'counter_id': config['counter_id'],
            'params': {
                'fields': config['hits_fields'],
                'start_date': config['start_date'],
                'end_date': config['end_date'],
            },
            'authenticator': authenticator
        }
        sessions_stream_args = {
            'counter_id': config['counter_id'],
            'params': {
                'fields': config['visits_fields'],
                'start_date': config['start_date'],
                'end_date': config['end_date'],
            },
            'authenticator': authenticator
        }
        return [Sessions(**sessions_stream_args), Views(**views_stream_args)]
 
    def evaluate(self, authenticator: TokenAuthenticator, counter_id: str, params: dict):
        url = f"{YandexMetricaStream.url_base}{counter_id}/logrequests/evaluate?date1={params['start_date']}&date2={params['end_date']}&source={params['source']}&fields="
        url += ','.join(params['fields'])

        headers = authenticator.get_auth_header()
        headers['Content-Type'] = 'application/x-ymetrika+json'
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 200 and data['log_request_evaluation']['possible']:
            return True, None
        return False, response.json()['errors']