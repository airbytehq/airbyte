from airbyte_cdk.models import SyncMode
from pytest import fixture
from source import (
    RmsCloudApiKapicheSource,
)


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(
        RmsCloudApiKapicheSource, "path", "v0/example_endpoint"
    )
    mocker.patch.object(
        RmsCloudApiKapicheSource, "primary_key", "test_primary_key"
    )
    mocker.patch.object(RmsCloudApiKapicheSource, "__abstractmethods__", set())
