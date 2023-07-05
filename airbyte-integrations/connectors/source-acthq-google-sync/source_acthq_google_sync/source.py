#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator, Mapping, Optional
from tqdm import tqdm
from traitlets import Any
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source
from source_acthq_google_sync.utils.acthq_helper import ActHQHelper
from source_acthq_google_sync.utils.s3_helper import S3Helper
from source_acthq_google_sync.utils.util_helper import UtilHelper
from source_acthq_google_sync.utils.gmail_helper import GMailHelper
  
            
class SourceActhqGoogleSync(Source):
   
    _primary_key = ['id']

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            self.actHQ = ActHQHelper(config=config)
            self.actHQ.test()
            s3 = S3Helper(config=config)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []
        from .schemas.gmail_schema import gmail_schema
        self.actHQ = ActHQHelper(config=config)
        stream = AirbyteStream(name=f"gmail-{self.actHQ.customer['name']}", 
                                     json_schema=json.loads(gmail_schema), 
                                     supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], 
                                     source_defined_cursor=True, 
                                     default_cursor_field=['historyId'], 
                                     cursor_field=['historyId'], 
                                     source_defined_primary_key=[["id"]],
                                     default_primary_key=[["id"]]
                                     )
        stream.primary_key = [['id']]
        streams.append(stream                                ) 
        return AirbyteCatalog(streams=streams)
        
    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        self.actHQ = ActHQHelper(config=config)
        self.gmail_helper = GMailHelper()
        util = UtilHelper()
        response = self.actHQ.get_user_list()
        slug = response['slug']
        customer_id = response['customerId']
        for user in tqdm(response['userList']):
            email = user['email']
            history_id = user['historyId'] if 'historyId' in user else '0'
            access_token = user["accessToken"]
            user_id = user['userId']
            messages = self.gmail_helper.get_all_messages(access_token=access_token, history_id=history_id, logger=logger, next_page_token=None)
            if 'history_id' in messages:
                history_id = self.set_history_id(history_id, messages['history_id'], email, state)
            for message in tqdm(messages["message_list"]):
                emailInbox = util.process_email_messages(email, config=config, logger=logger, message_id=message["id"], token=access_token, user=user, companyInfo={'slug': slug, 'customerId': customer_id})
                record = AirbyteRecordMessage(stream='gmail', data=emailInbox, emitted_at=int(datetime.now().timestamp()) * 1000)                        
                yield AirbyteMessage(type=Type.RECORD, record=record)
                if not history_id or int(emailInbox['historyId'])> int(history_id):
                    history_id = self.set_history_id(history_id,emailInbox['historyId'], email, state )
            self.actHQ.update_history_id(history_id=history_id, user_id=user_id)

    def set_history_id(self, old_history_id, new_history_id, email, state):
       if not old_history_id or int(new_history_id)> int(old_history_id):
            try:
                state[email] = new_history_id
                self._cursor_value[email] = new_history_id
            except AttributeError:
                self._cursor_value = {}
                self._cursor_value[email] = new_history_id
            return new_history_id
       return old_history_id
        
        
        