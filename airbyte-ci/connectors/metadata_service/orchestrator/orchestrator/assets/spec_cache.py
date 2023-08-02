from dagster import asset, AutoMaterializePolicy, FreshnessPolicy
import pandas as pd
from metadata_service.spec_cache import list_cached_specs
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "spec_cache"


@asset(
    group_name=GROUP_NAME,
    auto_materialize_policy=AutoMaterializePolicy.eager(max_materializations_per_minute=30),
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=1),
)
def cached_specs() -> OutputDataFrame:
    return output_dataframe(pd.DataFrame(list_cached_specs()))
