#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field
from airbyte_cdk.utils.spec_schema_transformations import resolve_refs


class OAuth2(BaseModel):
    client_id: str = Field(..., title="OAuth Client ID", description="OAuth2.0 client id", order=0)
    client_secret: str = Field(
        ..., title="OAuth Client Secret", description="OAuth2.0 client secret", airbyte_secret=True, order=1
    )

    class Config:
        title = "OAuth2.0 Credentials"
        schema_extra = {
            "description": "OAuth2.0 credentials used to authenticate admin actions (creating/deleting corpora)",
            "group": "auth",
        }

class VectaraConfig(BaseModel):
    oauth2: OAuth2
    customer_id: str = Field(..., title="Customer ID", description="Your customer id as it is in the authenticaion url", order=2, group="account")
    corpus_name: str = Field(..., title="Corpus Name", description="The Name of Corpus to load data into", order=3, group="account")

    class Config:
        title = "Vectara Config"
        schema_extra = {
            "description": "Configuration to connect to the Vectara instance",
            "groups": [
                {"id": "account", "title": "Account"},
                {"id": "auth", "title": "Authentication"},
            ]
        }

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = resolve_refs(schema)
        return schema