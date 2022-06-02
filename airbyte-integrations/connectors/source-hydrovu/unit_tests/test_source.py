#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock
#from unittest.mock import patch, mock
#from unittest import TestCase


from source_hydrovu.source import SourceHydrovu

#import responses
import pytest
from pytest import fixture

import requests
import requests_mock
import traceback

'''
###@pytest.fixture(name="config")
@pytest.fixture(name="config")
def config_fixture():
    config = {
        "client_id": "ABC",
        "client_secret": "secret",
    }

    return config
'''



@fixture
def config():
    return {"config": {"client_id": "ABC", "client_secret": "secret", }}


#class TestHydroVuSource(TestCase):
#    @patch('SourceHydrovu')



#@responses.activate
#def test_check_connection(mocker):
#def test_check_connection(mocker, config):
def test_check_connection(mocker, requests_mock, config):
    source = SourceHydrovu()
    logger_mock, config_mock = MagicMock(), MagicMock()
    #assert source.check_connection(logger_mock, config_mock) == (True, None)
    #assert source.check_connection(logger_mock, config=config) == (True, None)


    logger_mock = MagicMock()
   
    print ("logger_mock")
    print (logger_mock)

    requests_mock.post(
        #"https://www.hydrovu.com/public-api/v1/",
        'https://www.hydrovu.com/public-api/oauth/token',
        json=
            #{
            #    "type": "CONNECTION_STATUS", 
            #    "connectionStatus": {"status": "SUCCEEDED"},
            #    "aaa": "bbb"
            #}

            {'access_token': 'oMRyv5kYocI60byApqhmkD5sR2I', 'token_type': 'bearer', 'expires_in': 35999, 'scope': 'read:locations read:data'}

    )

    print ("requests_mock")
    print (requests_mock)

    print (source.check_connection(logger_mock, **config))

    print ("--------------")



    assert source.check_connection(logger_mock, **config) == (True, None)





    #ok, error_msg = source.check_connection(logger_mock, config=config)

    #assert False


    #assert ok
    #assert not error_msg
    #assert error_msg




'''
def test_streams(mocker):
    source = SourceHydrovu()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
'''
