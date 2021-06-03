import re

def valid_URL(test_str):
    pattern="(^[a-zA-Z0-9._-]*\.looker\.com$)|(^(?:[a-zA-Z0-9._-]*)?[a-zA-Z0-9._-]*\.[a-zA-Z0-9._-]*(?::\d{1,5})?$)|(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{1,5})?$)"
    result = re.match(pattern, test_str)
    if result is not None:
        return result.group(0)



#Defining tests below
def test_valid_URL_1():
    url="airbyte.looker.com"
    assert(valid_URL("airbyte.looker.com")==url)

def test_valid_URL_2():
    url="looker.airbyte.com"
    assert(valid_URL("looker.airbyte.com")==url)

def test_valid_URL_3():
    url="125.125.125.126:8009"
    assert(valid_URL("125.125.125.126:8009")==url)

def test_valid_URL_4():
    url="cooradial.sample.co.in"
    assert(valid_URL("cooradial.sample.co.in")==url)

def test_valid_URL_5():
    url="my.shiny.website.com:1234"
    assert(valid_URL("my.shiny.website.com:1234")==url)

def test_valid_URL_6():
    url="aeneas.mit.edu"
    assert(valid_URL("aeneas.mit.edu")==url)

def test_valid_URL_7():
    assert(valid_URL("suj.ki@fg")==None)     

def test_valid_URL_8():
    assert(valid_URL("www$google.com")==None)     




