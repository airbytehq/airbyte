import requests

class ActHQHelper:
    def __init__(self, config) -> None:
        self.backend_url = config["backendUrl"]
        self.backend_auth = config["backendAuth"]
        self.customer_instance_id = config['customerInstanceId']
        self.provider = 'google-mail' if config['isGmail'] else 'google-calendar'
        self.customer = self.get_customer()
       
    def get_customer(self):
        url = f'{self.backend_url}/gmail/inbox/customer?apiKey={self.backend_auth}&customerInstanceId={self.customer_instance_id}'
        response = requests.get(url)
        if not response:
            return None
        return response.json()
    
    def get_user_list(self):
        url = f'{self.backend_url}/gmail/inbox/user_list?apiKey={self.backend_auth}&customerInstanceId={self.customer_instance_id}&provider={self.provider}'
        user_list = requests.get(url)
        if not user_list:
            return None
        return user_list.json()
    
    def test(self):
        url = f'{self.backend_url}/gmail/inbox/test?apiKey={self.backend_auth}'
        response = requests.get(url)
        return response.json()
    
    def update_history_id(self, history_id, user_id):
        url = f'{self.backend_url}/gmail/inbox/history?apiKey={self.backend_auth}&userId={user_id}&historyId={history_id}'
        response = requests.patch(url=url)
        return response.json()
        
 