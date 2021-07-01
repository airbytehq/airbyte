
from typing import Any, Dict, Mapping 

import requests

class ZuoraAuthenticator:

    def __init__(self, is_sandbox: bool = True):
        self.is_sandbox = is_sandbox
    
    @property
    def endpoint(self) -> str:
        if self.is_sandbox == True:
            return "https://rest.apisandbox.zuora.com"
        else: 
            return "https://rest.zuora.com"

    # GENERATE TOKEN
    def generateToken(self, client_id: str, client_secret: str) -> Dict:
        endpoint = f"{self.endpoint}/oauth/token"
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": f"{client_id}", 
            "client_secret" : f"{client_secret}",
            "grant_type": "client_credentials",
            }
        try:
            session = requests.post(endpoint, headers=header, data=data)
            session.raise_for_status()
            return {
                "status": session.status_code,
                "header": {
                    "Authorization": f"Bearer {session.json().get('access_token')}", 
                    "Content-Type":"application/json", 
                    "X-Zuora-WSDL-Version": "107",
                    }
                }
        except requests.exceptions.HTTPError as e:
            return {"status": e}
