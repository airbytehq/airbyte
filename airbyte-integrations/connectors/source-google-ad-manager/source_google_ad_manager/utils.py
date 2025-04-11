import json
from datetime import datetime

from airbyte_cdk.models import (
    SyncMode,
    AirbyteStateMessage
)
from google.oauth2 import service_account
from googleads import ad_manager
from googleads import oauth2



def add_fields_to_schema(schema, fields, field_type="STRING"):
    for field in fields:
        field_name = field.strip('"')
        schema["properties"][field_name] = {"type": field_type}


def parse_date_to_dict(date):
    return {'year': date.year, 'month': date.month, 'day': date.day}


def get_start_date(state_date, config, today, sync_mode, date_format):
    config_start_date = config.get('startDate')
    if sync_mode == SyncMode.full_refresh:
        return datetime.strptime(config_start_date, date_format)
    return state_date or (datetime.strptime(config_start_date, date_format) if config_start_date else today)


def get_end_date(today, config, sync_mode, date_format):
    if sync_mode == SyncMode.incremental:
        return today
    config_end_date = config.get('endDate')
    return datetime.strptime(config_end_date, date_format) if config_end_date else today


def create_ad_manager_client(config, scopes, application_name):
    service_account_info = json.loads(config["service_account"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scopes)
    oauth2_client = oauth2.GoogleCredentialsClient(credentials=credentials)
    return ad_manager.AdManagerClient(oauth2_client, network_code=config["network_code"],
                                      application_name=application_name)


def get_state(state):
    state_date, start_chunk_index = None, 0
    if state:
        for state_message in state:
            # Se state_message è già un dizionario
            if isinstance(state_message, dict):
                if "stream" in state_message and state_message["stream"] and "stream_state" in state_message["stream"]:
                    stream_state = state_message["stream"]["stream_state"]
                    state_date = stream_state.get("state_date")
                    start_chunk_index = stream_state.get("start_chunk_index", 0)
            else:
                # Se è un oggetto AirbyteStateMessage
                if hasattr(state_message, "stream") and state_message.stream and hasattr(state_message.stream, "stream_state"):
                    stream_state = state_message.stream.stream_state
                    if isinstance(stream_state, dict):
                        state_date = stream_state.get("state_date")
                        start_chunk_index = stream_state.get("start_chunk_index", 0)
                    else:
                        state_date = getattr(stream_state, "state_date", None)
                        start_chunk_index = getattr(stream_state, "start_chunk_index", 0)
    return state_date, start_chunk_index


def update_report_job_config(report_job, config, keys):
    for key in keys:
        if key in config:
            report_job['reportQuery'][key] = config[key]
    return report_job
