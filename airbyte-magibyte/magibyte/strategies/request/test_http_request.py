import unittest

from magibyte.strategies.request import HttpRequest


class TestHttpRequest(unittest.TestCase):
    def test_build(self):
        options = {
            'base_url': 'test',
            'method': 'get',
            'params': [
                {
                    'name': 'param_abc',
                    'value': 'value_param_abc',
                },
                {
                    'name': 'param_abc',
                    'value': 'value_param_abc_2',
                },
                {
                    'name': 'param_def',
                    'value': '',
                    'on_empty': 'skip'
                },
                {
                    'name': 'param_empty',
                    'value': '',
                },
            ],
            'headers': [
                {
                    'name': 'header_abc',
                    'value': 'value_header_abc',
                },
                {
                    'name': 'header_abc',
                    'value': 'value_header_abc_2',
                },
                {
                    'name': 'header_def',
                    'value': '',
                    'on_empty': 'skip'
                },
                {
                    'name': 'header_empty',
                    'value': '',
                },
            ]
        }
        request = HttpRequest(options).build()

        self.assertEqual(request, {
            'url': 'test',
            'method': 'get',
            'headers': [
                ('header_abc', 'value_header_abc'),
                ('header_abc', 'value_header_abc_2')
                ('header_empty', '')
            ],
            'params': [
                ('param_abc', 'value_param_abc')
                ('param_abc', 'value_param_abc_2')
                ('param_empty', '')
            ]
        })


if __name__ == '__main__':
    unittest.main()
