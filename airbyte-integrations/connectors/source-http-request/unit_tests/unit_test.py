#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import unittest

from source_http_request import SourceHttpRequest
from unittest.mock import patch, Mock
from datetime import date

class TestSourceHttpRequest(unittest.TestCase):
    def test_simple_parse_config_success(self):
        config = {
            "http_method": "get",
            "url": "http://api.bart.gov/api",
            "headers": '{"Content-Type": "application/json"}',
            "body": '{"something": "good"}',
        }

        source = SourceHttpRequest()
        actual = source._parse_config(config)
        expected = {
            "http_method": "get",
            "url": "http://api.bart.gov/api",
            "headers": {"Content-Type": "application/json"},
            "body": {"something": "good"},
            "response_format": "json",
        }
        self.assertEqual(expected, actual)
    
    @patch("source_http_request.source.datetime")
    def test_date_parse_config_success(self, mock_date):
        mock_date.today.return_value = date(2021, 8, 1)
        config = {
            "http_method": "get",
            "url": "http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{month_year}.csv",
            "headers": '{"Content-Type": "application/json"}',
            "body": '{"something": "good"}',
            "params": "[{\"type\": \"date\", \"unit\": \"month\", \"format\": \"%Y%m\", \"variable\": \"month_year\", \"value\": \"current\"}]"
        }

        source = SourceHttpRequest()
        actual = source._parse_config(config)
        expected = {
            "http_method": "get",
            "url": "http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_202108.csv",
            "headers": {"Content-Type": "application/json"},
            "body": {"something": "good"},
            "response_format": "json",
        }
        self.assertEqual(expected, actual)

    @patch("source_http_request.source.datetime")
    def test_period_parse_config_success(self, mock_date):
        mock_date.today.return_value = date(2021, 8, 1)
        config = {
            "http_method": "get",
            "url": "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda=%27AUD%27&@dataInicial=%27{from}%27&@dataFinalCotacao=%27{to}%27&$format=json",
            "headers": '{"Content-Type": "application/json"}',
            "body": '{"something": "good"}',
            "params": "[{\"type\": \"period\", \"unit\": \"day\", \"format\": \"%m-%d-%Y\", \"start_date\": {\"variable\": \"from\", \"value\": \"current - 1\"}, \"end_date\": {\"variable\": \"to\", \"value\": \"current + 1\"}}]"
        }

        source = SourceHttpRequest()
        actual = source._parse_config(config)
        expected = {
            "http_method": "get",
            "url": "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda=%27AUD%27&@dataInicial=%2707-31-2021%27&@dataFinalCotacao=%2708-02-2021%27&$format=json",
            "headers": {"Content-Type": "application/json"},
            "body": {"something": "good"},
            "response_format": "json",
        }
        print(actual["url"])
        self.assertEqual(expected, actual)
