
import pytest
from unittest.mock import MagicMock, patch
from source_zoho_desk.streams import ZohoStreamFactory
from source_zoho_desk.types_zoho import ModuleMeta

MOCK_CONFIG = {"key": "value"}

@pytest.fixture
def mock_zoho_api():
    with patch('source_zoho_desk.streams.ZohoAPI') as MockZohoAPI:
        yield MockZohoAPI

@pytest.fixture
def mock_module_meta():
    with patch('source_zoho_desk.types_zoho.ModuleMeta.from_dict') as MockModuleMeta:
        MockModuleMeta.return_value = ModuleMeta(
            api_name='moduleApiName', 
            module_name='Module Name',
            api_supported=True,
            fields=[]
        )
        yield MockModuleMeta

@pytest.fixture
def factory(mock_zoho_api, mock_module_meta):
    mock_zoho_api_instance = mock_zoho_api.return_value
    mock_zoho_api_instance.modules_settings.return_value = [{'apiName': 'moduleApiName'}]  
    mock_zoho_api_instance.module_settings.return_value = {}
    mock_zoho_api_instance.max_concurrent_requests = 5
    return ZohoStreamFactory(config=MOCK_CONFIG)

def test_init_modules_meta(factory, mock_zoho_api):
    modules_meta = factory._init_modules_meta()
    assert len(modules_meta) == 1
    assert modules_meta[0].api_name == 'moduleApiName'  

def test_populate_module_meta(factory, mock_zoho_api):
    module = ModuleMeta(api_name='module1', module_name='Module 1', api_supported=True)
    factory._populate_module_meta(module)
    mock_zoho_api.return_value.module_settings.assert_called_once_with('module1')

def test_produce(factory, mock_zoho_api):
    with patch('source_zoho_desk.streams.concurrent.futures.ThreadPoolExecutor') as MockExecutor:
        mock_executor_instance = MockExecutor.return_value.__enter__.return_value
        mock_executor_instance.map = MagicMock()

        streams = factory.produce()

        mock_zoho_api.return_value.modules_settings.assert_called_once()
        assert len(streams) == 1
        assert isinstance(streams[0], ModuleMeta)
