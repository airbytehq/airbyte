import re
import unittest

def valid_URL(test_str):
    pattern="(^[a-zA-Z0-9._-]*\.looker\.com$)|(^(?:[a-zA-Z0-9._-]*)?[a-zA-Z0-9._-]*\.[a-zA-Z0-9._-]*(?::\d{1,5})?$)|(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{1,5})?$)"
    result = re.match(pattern, test_str)
    if result is not None:
        return result.group(0)



class TestURLPattern(unittest.TestCase):

    def test_valid_URL_1(self):
        url="airbyte.looker.com"
        self.assertEqual(valid_URL("airbyte.looker.com"),url)

    def test_valid_URL_2(self):
        url="looker.airbyte.com"
        self.assertEqual(valid_URL("looker.airbyte.com"),url)

    def test_valid_URL_3(self):
        url="125.125.125.126:8009"
        self.assertEqual(valid_URL("125.125.125.126:8009"),url)

    def test_valid_URL_4(self):
        url="cooradial.sample.co.in"
        self.assertEqual(valid_URL("cooradial.sample.co.in"),url)
    
    def test_valid_URL_5(self):
        url="my.shiny.website.com:1234"
        self.assertEqual(valid_URL("my.shiny.website.com:1234"),url)

    def test_valid_URL_6(self):
        url="aeneas.mit.edu"
        self.assertEqual(valid_URL("aeneas.mit.edu"),url)

    def test_valid_URL_7(self):
        self.assertEqual(valid_URL("suj.ki@fg"),None)     

    def test_valid_URL_8(self):
        self.assertEqual(valid_URL("www$google.com"),None)     

        
