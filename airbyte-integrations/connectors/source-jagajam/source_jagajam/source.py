#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta
import json
from time import strptime
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from .streams import Communities, ReachCount, UsersCount, Posts, Benchmarks


class SourceJagajam(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def transform_config_date_range(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range: Mapping[str, Any] = config.get('date_range', {})
        date_range_type: str = date_range.get('date_range_type')
        date_from: datetime = None
        date_to: datetime = None
        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_user_date_format = "%Y-%m-%d"

        if date_range_type == "custom_date":
            date_from = strptime(date_range.get(
                'date_from'), from_user_date_format)
            date_to = strptime(date_range.get(
                'date_to'), from_user_date_format)
        elif date_range_type == 'from_start_date_to_today':
            date_from = strptime(date_range.get(
                'date_from'), from_user_date_format)
            if date_range.get('should_load_today'):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)
        elif date_range_type == 'last_n_days':
            date_from = today_date - \
                timedelta(date_range.get('last_days_count'))
            if date_range.get('should_load_today'):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)

        config['date_from_transformed'], config['date_to_transformed'] = date_from, date_to
        return config

    @staticmethod
    def prepare_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = SourceJagajam.transform_config_date_range(config)
        config['custom_constants'] = json.loads(
            config.get('custom_constants_json', '{}'))
        return config

    def get_available_communities(self, config):
        auth_stream_args = {
            'auth_token': config['auth_token'],
        }
        constants_stream_args = {
            'client_name': config.get('client_name_constant', ''),
            'product_name': config.get('product_name_constant', ''),
            'custom_constants': config.get('custom_constants', {}),
        }
        communities_stream_instance = Communities(
            **auth_stream_args, **constants_stream_args)
        return list(communities_stream_instance.read_records(sync_mode=SyncMode.full_refresh))

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = SourceJagajam.prepare_config(config)
        chunks_config = config.get('chunks', {
            "chunk_mode_type": "dont_split"
        })
        auth_stream_args = {
            'auth_token': config['auth_token'],
        }
        constants_stream_args = {
            'client_name': config.get('client_name_constant', ''),
            'product_name': config.get('product_name_constant', ''),
            'custom_constants': config.get('custom_constants', {}),
        }
        communities_details_stream_args = {
            **auth_stream_args,
            'date_from': config['date_from_transformed'],
            'date_to': config['date_to_transformed'],
            'date_granuilarity': 'day',
            'chunks_config': chunks_config,
            'available_communities': self.get_available_communities(config),
            **constants_stream_args,
        }
        return [
            Communities(**auth_stream_args, **constants_stream_args),
            ReachCount(**communities_details_stream_args),
            UsersCount(**communities_details_stream_args),
            Benchmarks(**communities_details_stream_args),
            Posts(**communities_details_stream_args),
        ]
