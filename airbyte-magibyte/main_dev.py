"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import sys

from magibyte.models.source import Source

logging.basicConfig(level=logging.DEBUG)

states = {}

config = {
    'config': {
        'base': 'USD',
        'start_date': '2020-01-01'
    },
    'resources': [{
        'rate': {
            'var': {
                'name': 'abc'
            },

        }
    }]
}


def emit_record(stream, record):
    logging.debug(record)


def emit_state(stream, state):
    states[stream.name] = state


def cleanup():
    logging.debug(states)


def main():
    source = Source()

    for stream in source:
        for record, state in stream:
            emit_record(stream, record)
            emit_state(stream, state)

    cleanup()

    #
    # context = {
    #     'config': {
    #         'base': 'USD',
    #         'start_date': '2020-01-01'
    #     },
    #     'state': {
    #         'last_date': '2021-01-01'
    #     }
    # }
    #
    # pagination = SinglePagination({})
    # request_builder = HttpRequest(TransformDict({
    #     'base_url': 'https://api.exchangeratesapi.io/{{ state.last_date or config.start_date }}?base={{ config.base }}'
    # }, lambda v: extrapolate(v, context)))
    #
    # for page in pagination:
    #     logging.debug(f"Paginating {page}")
    #
    #     request = {}
    #
    #     context['previous_page'] = context.get('page')
    #     context['page'] = page
    #
    #     context['previous_request'] = context.get('request')
    #     context['request'] = request_builder.build()
    #
    #     requests.request(
    #         method=request.get('method', 'get'),
    #         url=self.options['base_url'])
    #
    #     response = make_request(request)
    #     data = extract_data(response)
    #     for entry in data:
    #         emit(entry)
    #
    # #
    # #
    # # http_options = TransformDict({
    # #     'base_url': 'https://api.exchangeratesapi.io/{{ state.last_date or config.start_date }}?base={{ config.base }}'
    # # }, lambda v: extrapolate(v, context))
    # #
    # #
    # # response = operations.http.HttpRequest(http_options).execute(context)
    # # logging.debug(response.json())


if __name__ == "__main__":
    logging.info(f"Starting Magibyte {sys.argv}")
    main()
