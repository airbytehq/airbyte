
from typing import Any, Mapping 

import requests

class ZuoraAuthenticator:

    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox
    
    @property
    def endpoint(self) -> str:
        if self.is_sandbox == True:
            return "https://rest.apisandbox.zuora.com"
        else: 
            return "https://rest.zuora.com"

    # GENERATE TOKEN
    def generateToken(self):
        endpoint = f"{self.endpoint}/oauth/token"
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": f"{self.client_id}", 
            "client_secret" : f"{self.client_secret}",
            "grant_type": "client_credentials",
            }
        try:
            session = requests.post(endpoint, headers=header, data=data)
            session.raise_for_status()
            token = session.json().get("access_token")
            return {
                "status": session.status_code,
                "token": token, 
                "header": {
                    "Authorization": f"Bearer {token}", 
                    "Content-Type":"application/json", 
                    "X-Zuora-WSDL-Version": "107",
                    }
                }
        except requests.exceptions.HTTPError as e:
            return {"status": e}
