#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional
from pydantic import BaseModel, Field


class SnowflakeCortexConfig(BaseModel):
    # to-do: split the fields into authentication & processing sections  
    account: str = Field(
        ...,
        title="Account",
        airbyte_secret=True,
        description="Enter the account name you want to use to access the database.",
        examples=["xxx.us-east-2.aws"]
    )
    username: str = Field(
        ..., 
        title="Username", 
        airbyte_secret=True,
        description="Enter the name of the user you want to use to access the database", 
        examples=["AIRBYTE_USER"]
    )
    password: str = Field(
        ..., 
        title="Password", 
        airbyte_secret=True, 
        description="Enter the password associated with the user you entered above"
    )
    database: str = Field(
        ...,
        title="Database",
        airbyte_secret=True,
        description="Enter the name of the database that you want to sync data into",
        examples=["AIRBYTE_DATABASE"]
    )
    warehouse: str = Field(
        ..., 
        title="Warehouse", 
        airbyte_secret=True, 
        description="Enter the name of the warehouse that you want to sync data into", 
        examples=["AIRBYTE_WAREHOUSE"]
    )
    role: str = Field(
        ..., 
        title="Role", 
        airbyte_secret=True, 
        description="Enter the name of the role that you want to sync data into", 
        examples=["AIRBYTE_ROLE", "ACCOUNTADMIN"]
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
        title = "authentication"
        schema_extra = {
            "description": "Configuration to connect to the Snowflake instance",
            "group": "Authentication",
        }

