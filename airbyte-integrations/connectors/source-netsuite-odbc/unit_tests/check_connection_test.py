
import pytest
import logging
from source_netsuite_odbc import SourceNetsuiteOdbc
from datetime import datetime


@pytest.fixture
def flawed_config():
    return {
      "service_host": "aaaaaa-sb1.connect.api",
      "service_port": "1708",
      "account_id": "aaaaaaa_SB1",
      "consumer_key": "0b6c796a-e4d4-4bd9-adf5-e4a63d8d8c15",
      "consumer_secret": "f92911a7-9667-4b7a-b99d-e1bd0024434f",
      "token_key": "87ab1c97-1034-4845-bbf0-104b27152acc",
      "token_secret": "4efe5c11-cd09-404b-accb-1d1e48492816"
    }

@pytest.fixture
def flawed_config_two():
    return {
      "service_host": "aaaaaa-sb1.connect.api.netsuite.com",
      "service_port": "1708",
      "account_id": "aaaaaaa_SB1",
      "consumer_key": "0b6c796a-e4d4-4bd9-adf5-e4a63d8d8c15",
      "consumer_secret": "f92911a7-9667-4b7a-b99d-e1bd0024434f",
      "token_key": "87ab1c97-1034-4845-bbf0-104b27152acc",
      "token_secret": "4efe5c11-cd09-404b-accb-1d1e48492816",
      "starting_year": 1899
    }

@pytest.fixture
def logger():
  return logging.getLogger("airbyte")

def test_invalid_service_host(logger, flawed_config):
  source = SourceNetsuiteOdbc()
  result = source.check_connection(logger, flawed_config)
  assert result[0] == False
  assert result[1] == "Invalid service_host: aaaaaa-sb1.connect.api.  Must be of the form: *******.connect.api.netsuite.com"
     

def test_invalid_starting_year(logger, flawed_config_two):
  source = SourceNetsuiteOdbc()
  result = source.check_connection(logger, flawed_config_two)
  assert result[0] == False
  assert result[1] == f"Invalid starting_year: {1899}.  Must be between 1900 and {datetime.now().year}"
     
