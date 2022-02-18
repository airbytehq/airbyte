from typing import Dict

from airbyte_cdk.models import DestinationSyncMode
from destination_redshift_py.table import Table
from pydantic.main import BaseModel


class Stream(BaseModel):
    name: str
    destination_sync_mode: DestinationSyncMode
    final_tables: Dict[str, Table]
    staging_tables: Dict[str, Table] = dict()

    class Config:
        arbitrary_types_allowed = True
