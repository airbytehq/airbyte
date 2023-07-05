import requests

class GMailHelper:
    def __init__(self) -> None:
        self.message_set = {}
        self.next_page_token = None
        
    GMAIL_BASE_URL = 'https://www.googleapis.com/gmail/v1/users/me'
    def get_message(self, accessToken, message_id, logger):
        try:
            url = f'{self.GMAIL_BASE_URL}/messages/{message_id}?access_token={accessToken}'
            inbox_call = requests.get(url)
            inbox = inbox_call.json()
            return inbox
        except Exception as err:
            reason = f"Failed to read data of {message_id}"
            logger.error(reason)
            raise err   
    
    def get_all_messages(self, access_token: str, history_id: str, logger, next_page_token):
        if history_id:
            return self.get_messages_by_history_id(access_token=access_token, history_id=history_id, logger=logger)
        message_list = self.get_message_list(access_token=access_token, next_page_token=next_page_token, logger=logger)
        if 'nextPageToken' in message_list:
            self.next_page_token = message_list['nextPageToken']
        else: 
            self.next_page_token = None
        return {'message_list': message_list['messages']}
    
   
    def get_message_list(self, access_token, next_page_token, logger):
        try:
            print('get_message_list')
            url = f'{self.GMAIL_BASE_URL}/messages?access_token={access_token}&maxResults=500'
            if next_page_token:
                url = f'{url}&pageToken=${next_page_token}'
            inbox_call = requests.get(url)
            messages = inbox_call.json()
            if 'nextPageToken' in messages:
                result = self.get_message_list(access_token=access_token, next_page_token=messages['nextPageToken'], logger=logger)
                messages['messages'].update(result['messages'])
            return messages
        except Exception as err:
            reason = f"Failed to read message_id"
            logger.error(reason)
            raise err  

    def get_messages_by_history_id(self, access_token, history_id, logger):
        try:
            print('get_messages_by_history_id')
            url = f'{self.GMAIL_BASE_URL}/history?access_token={access_token}&startHistoryId={history_id}'
            response = requests.get(url)
            return self._process_history_response(response.json())
        except Exception as err:
            reason = f"Failed to read message_id"
            logger.error(reason)
            raise err 
    
    def _process_history_response(self, value):
        message_list = []
        history_id = value['historyId']
        if 'history' in value and type (value['history']) == list:
            for history in value['history']:
                if history['messages'] and type (history['messages']) == list:
                    for message in history['messages']:
                        if message['id'] not in self.message_set:
                            self.message_set[message['id']] = 1
                            message_list.append(message)

        return {"history_id": history_id, 'message_list': message_list}