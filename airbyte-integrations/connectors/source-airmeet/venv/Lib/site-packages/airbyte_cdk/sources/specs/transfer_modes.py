#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Literal

from pydantic.v1 import AnyUrl, BaseModel, Field

from airbyte_cdk import OneOfOptionConfig


class DeliverPermissions(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Replicate Permissions ACL"
        description = "Sends one identity stream and one for more permissions (ACL) streams to the destination. This data can be used in downstream systems to recreate permission restrictions mirroring the original source."
        discriminator = "delivery_type"

    delivery_type: Literal["use_permissions_transfer"] = Field(
        "use_permissions_transfer", const=True
    )

    include_identities_stream: bool = Field(
        title="Include Identity Stream",
        description="This data can be used in downstream systems to recreate permission restrictions mirroring the original source",
        default=True,
    )
