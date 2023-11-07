#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field



class OAuth2(BaseModel):
    client_id: str = Field(..., title="Client ID", description="OAuth2.0 client id", order=0)
    client_secret: str = Field(
        ..., title="Client Secret", description="OAuth2.0 client secret", airbyte_secret=True, order=1
    )

    class Config:
        title = "OAuth2.0 Credentials"
        schema_extra = {"description": "OAuth2.0 credentials used to authenticate admin actions (creating/deleting corpora)"}

class VectaraConfig(BaseModel):
    oauth2: OAuth2 = Field(
        ..., title="OAuth2.0 Credentials", description="OAuth2.0 credentials used to authenticate admin actions (creating/deleting corpora)", type="object", order=1
    )
    customer_id: str = Field(..., title="Customer ID", description="Your customer id as it is in the authenticaion url", order=2)
    corpus_name: str = Field(..., title="Corpus Name", description="The Name of Corpus to load data into", order=2)
    # corpus_id: Optional[int] = Field(default="", title="Corpus ID", description="The ID of Corpus to load data into", order=3)

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "indexing",
            "description": "Indexing configuration",
        }
