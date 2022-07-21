from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import SyncMode
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
            views_stream = Views(**{
                'counter_id': config['counter_id'],
                'params': {
                    'fields': config['hits_fields'],
                    'start_date': config['start_date'],
                    'end_date': config['end_date']
                },
                'authenticator': TokenAuthenticator(token=config["auth_token"]),
            })
            sessions_stream = Sessions(**{
                'counter_id': config['counter_id'],
                'params': {
                    'fields': config['visits_fields'],
                    'start_date': config['start_date'],
                    'end_date': config['end_date']
                },
                'authenticator': TokenAuthenticator(token=config["auth_token"]),
            })
            next(views_stream.read_records(sync_mode=SyncMode.full_refresh))
            next(sessions_stream.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[YandexMetricaStream]:
        views_stream_args = {
            'counter_id': config['counter_id'],
            'params': {
                'fields': config['hits_fields'],
                'start_date': config['start_date'],
                'end_date': config['end_date'],
            },
            'authenticator': TokenAuthenticator(token=config["auth_token"])
        }
        sessions_stream_args = {
            'counter_id': config['counter_id'],
            'params': {
                'fields': config['visits_fields'],
                'start_date': config['start_date'],
                'end_date': config['end_date'],
            },
            'authenticator': TokenAuthenticator(token=config["auth_token"])
        }
        return [Views(**views_stream_args), Sessions(**sessions_stream_args)]
 

