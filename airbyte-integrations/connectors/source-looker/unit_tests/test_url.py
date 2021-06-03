import re
import pytest

def valid_url(test_str):
    pattern="(^[a-zA-Z0-9._-]*\.looker\.com$)|(^(?:[a-zA-Z0-9._-]*)?[a-zA-Z0-9._-]*\.[a-zA-Z0-9._-]*(?::\d{1,5})?$)|(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{1,5})?$)"
    result = re.match(pattern, test_str)
    if result is not None:
        return result.group(0)

@pytest.fixture
def url():
    url=["airbyte.looker.com","looker.airbyte.com",
         "125.125.125.126:8009","cooradial.sample.co.in",
         "my.shiny.website.com:1234","aeneas.mit.edu",   
        ]
    return url


#Defining tests below
def test_valid_url_1(url):
    assert(valid_url("airbyte.looker.com")==url[0])

def test_valid_url_2(url):
    assert(valid_url("looker.airbyte.com")==url[1])

def test_valid_url_3(url):
    assert(valid_url("125.125.125.126:8009")==url[2])

def test_valid_url_4(url):
    assert(valid_url("cooradial.sample.co.in")==url[3])

def test_valid_url_5(url):
    assert(valid_url("my.shiny.website.com:1234")==url[4])

def test_valid_url_6(url):
    assert(valid_url("aeneas.mit.edu")==url[5])

def test_valid_url_7(url):
    assert(valid_url("suj.ki@fg")==None)     

def test_valid_url_8(url):
    assert(valid_url("www$google.com")==None)     




