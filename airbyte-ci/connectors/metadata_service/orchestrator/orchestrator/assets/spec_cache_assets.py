from dagster import asset
import pandas as pd
from metadata_service.spec_cache import list_cached_specs
from ..utils.dagster_helpers import OutputDataFrame


GROUP_NAME = "spec_cache"


@asset(group_name=GROUP_NAME)
def cached_specs():
    return OutputDataFrame(pd.DataFrame(list_cached_specs()))
