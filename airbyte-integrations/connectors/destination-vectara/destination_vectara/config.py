#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from airbyte_cdk.utils.spec_schema_transformations import resolve_refs
from pydantic import BaseModel, Field


class OAuth2(BaseModel):
    client_id: str = Field(..., title="OAuth Client ID", description="OAuth2.0 client id", order=0)
    client_secret: str = Field(..., title="OAuth Client Secret", description="OAuth2.0 client secret", airbyte_secret=True, order=1)

    class Config:
        title = "OAuth2.0 Credentials"
        schema_extra = {
            "description": "OAuth2.0 credentials used to authenticate admin actions (creating/deleting corpora)",
            "group": "auth",
        }


class VectaraConfig(BaseModel):
    oauth2: OAuth2
    customer_id: str = Field(
        ..., title="Customer ID", description="Your customer id as it is in the authenticaion url", order=2, group="account"
    )
    corpus_name: str = Field(..., title="Corpus Name", description="The Name of Corpus to load data into", order=3, group="account")

    parallelize: Optional[bool] = Field(
        default=False,
        title="Parallelize",
        description="Parallelize indexing into Vectara with multiple threads",
        always_show=True,
        group="account",
    )

    text_fields: Optional[List[str]] = Field(
        default=[],
        title="Text fields to index with Vectara",
        description="List of fields in the record that should be in the section of the document. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered text fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.",
        always_show=True,
        examples=["text", "user.name", "users.*.name"],
    )
    title_field: Optional[str] = Field(
        default="",
        title="Text field to use as document title with Vectara",
        description="A field that will be used to populate the `title` of each document. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered text fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.",
        always_show=True,
        examples=["document_key"],
    )
    metadata_fields: Optional[List[str]] = Field(
        default=[],
        title="Fields to store as metadata",
        description="List of fields in the record that should be stored as metadata. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered metadata fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array. When specifying nested paths, all matching values are flattened into an array set to a field named by the path.",
        always_show=True,
        examples=["age", "user"],
    )

    class Config:
        title = "Vectara Config"
        schema_extra = {
            "description": "Configuration to connect to the Vectara instance",
            "groups": [
                {"id": "account", "title": "Account"},
                {"id": "auth", "title": "Authentication"},
            ],
        }

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = resolve_refs(schema)
        return schema
