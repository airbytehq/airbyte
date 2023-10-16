import pytest


@pytest.fixture(autouse=True)
def patch_sleep(mocker):
    mocker.patch("time.sleep")
