"""CI Workflow settings for Airbyte Java CDK"""

from aircmd.models.base import GlobalSettings
from pydantic import Field


class JavaCDKSettings(GlobalSettings):
    version: str = Field("dev", env="VERSION")
    dagger: bool = Field(True, env="DAGGER")
    sub_build: str = Field("CONNECTORS_BASE", env="SUB_BUILD")
