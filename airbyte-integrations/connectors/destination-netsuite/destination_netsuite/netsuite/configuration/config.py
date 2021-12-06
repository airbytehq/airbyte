
import re
from pydantic import BaseModel


__all__ = ("Config", "TokenAuth")

class TokenAuth(BaseModel):
    consumer_key: str
    consumer_secret: str
    token_id: str
    token_secret: str

class Config(BaseModel):
    base_url: str
    token_auth: TokenAuth

    def get_account_id(self) -> str:
        # group index         #1         #2    #3
        match = re.search(r'^(https://)?(\d+)?(\.suitetalk\.api\.netsuite\.com)', self.base_url)
        if match is not None:
            return match.group(2) # from group index
        else:
            raise Exception("No match! Check hostname.")