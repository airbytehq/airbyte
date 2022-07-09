from typing import TypedDict


class Spec(TypedDict):
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
