import pytest

from source_netsuite_odbc.odbc_utils import NetsuiteODBCCursorConstructor
from source_netsuite_odbc.errors import generate_host_resolution_error_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

@pytest.fixture
def config_one():
    return {
      "service_host": "aaaaaa-sb1.connect.api.netsuite.com",
      "service_port": "1708",
      "account_id": "aaaaaaa_SB1",
      "consumer_key": "0b6c796a-e4d4-4bd9-adf5-e4a63d8d8c15",
      "consumer_secret": "f92911a7-9667-4b7a-b99d-e1bd0024434f",
      "token_key": "87ab1c97-1034-4845-bbf0-104b27152acc",
      "token_secret": "4efe5c11-cd09-404b-accb-1d1e48492816"
    }

  
@pytest.fixture
def config_two():
    return {
      "service_host": "bbbbbb-sb1.connect.api.netsuite.com",
      "service_port": "1708",
      "account_id": "bbbbbbb_SB1",
      "consumer_key": "06beb54f-f872-4107-90f0-97d26c2909ce",
      "consumer_secret": "1f9a4ea1-7c5f-4b45-a2b5-d6bd1b7b6667",
      "token_key": "b75375ca-8c09-416e-825a-53a20138f74a",
      "token_secret": "74697aaa-fa9e-4254-aa7a-c4505034e4bc"
    }

CONNECTION_STRING_ONE = 'DRIVER=NetSuite ODBC Drivers 8.1;Host=aaaaaa-sb1.connect.api.netsuite.com;Port=1708;Encrypted=1;AllowSinglePacketLogout=1;Truststore=/opt/netsuite/odbcclient/cert/ca3.cer;ServerDataSource=NetSuite2.com;UID=TBA;PWD=aaaaaaa_SB1&0b6c796a-e4d4-4bd9-adf5-e4a63d8d8c15&87ab1c97-1034-4845-bbf0-104b27152acc&11111&1701469921&25CcuGJ99s52zKpeIvGno5SE2e7eF6/w/I05nElY8Bo=&HMAC-SHA256;CustomProperties=AccountID=aaaaaaa_SB1;RoleID=57;StaticSchema=1'
CONNECTION_STRING_TWO = 'DRIVER=NetSuite ODBC Drivers 8.1;Host=bbbbbb-sb1.connect.api.netsuite.com;Port=1708;Encrypted=1;AllowSinglePacketLogout=1;Truststore=/opt/netsuite/odbcclient/cert/ca3.cer;ServerDataSource=NetSuite2.com;UID=TBA;PWD=bbbbbbb_SB1&06beb54f-f872-4107-90f0-97d26c2909ce&b75375ca-8c09-416e-825a-53a20138f74a&11111&1701469921&ZSiCPmuDhechNjPTiP12NWu5JBhzeOh113xqLxsq77w=&HMAC-SHA256;CustomProperties=AccountID=bbbbbbb_SB1;RoleID=57;StaticSchema=1'

class TestNetsuiteODBCCursorConstructor:

  def test_db_connection_is_built_correctly(self, config_one, config_two, monkeypatch):
    # nonce will return a random value, so we overwrite it with a constant.
    def mock_nonce_return(self):
      return '11111'
    
    def mock_timestamp_return(self):
       return '1701469921'
    
    monkeypatch.setattr(NetsuiteODBCCursorConstructor, "generate_nonce", mock_nonce_return)
    monkeypatch.setattr(NetsuiteODBCCursorConstructor, "generate_timestamp", mock_timestamp_return)

    constructor = NetsuiteODBCCursorConstructor()

    connection_string_one = constructor.construct_db_string(config_one)

    connection_string_two = constructor.construct_db_string(config_two)

    assert connection_string_one == CONNECTION_STRING_ONE
    assert connection_string_two == CONNECTION_STRING_TWO
  
  def test_properly_handled_failure_for_host_resolution_failure(self, config_one):
    try:
      constructor = NetsuiteODBCCursorConstructor()
      constructor.create_database_connection(config_one)
    except Exception as e:
      assert e.message == generate_host_resolution_error_message(config_one["service_host"])

  def test_nonce_generation_is_10_characters(self):
    constructor = NetsuiteODBCCursorConstructor()
    nonce = constructor.generate_nonce()
    assert len(nonce) == 10

  def test_nonce_generation_is_random(self):
    constructor = NetsuiteODBCCursorConstructor()
    nonce_one = constructor.generate_nonce()
    nonce_two = constructor.generate_nonce()
    nonce_three = constructor.generate_nonce()

    are_all_nonces_equal = nonce_one == nonce_two and nonce_two == nonce_three

    assert not are_all_nonces_equal 