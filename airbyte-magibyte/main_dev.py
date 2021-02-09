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

import yaml

from magibyte.core import strategy_builder
from magibyte.core.extrapolation import extrapolate
from magibyte.operations.extract.http_resource_extract import HttpResourceExtract

logging.basicConfig(level=logging.DEBUG)

states = {}

config = yaml.safe_load('''
config:
  base: USD
  start_date: 2021-01-01

streams:
  rate:
    extract:
      strategy: magibyte.operations.extract.HttpResource
      options:
        request:
          strategy: magibyte.operations.request.HttpRequest
          options:
            base_url: "https://api.exchangeratesapi.io/{{ page.current_date.format('YYYY-MM-DD') }}"
            method: get
            params:
            - name: base
              value: "{{ config.base }}"
        decoder:
          strategy: magibyte.operations.decode.Json
        selector:
          strategy: magibyte.operations.select.JsonPath
          options:
            path: $.rates
        pagination:
          strategy: magibyte.operations.pagination.Datetime
          options:
            start_date: "{{ state.date | default(config.start_date) }}"
            start_inclusive: "{{ state.date | default(true) }}"
            end_date: "{{ now_local() }}"
            end_inclusive: true
            step: 1d
        state:
          strategy: magibyte.operations.state.Context
          options:
            name: date
            value: "{{ page.current_date.format('YYYY-MM-DD') }}"
''')


def emit_record(stream, record):
    logging.debug(record)


def emit_state(stream, state):
    states[stream.name] = state


def cleanup():
    logging.debug(states)


def main():
    logging.debug(config)

    context = {
        'config': config['config'],
        'state': {'date': '2021-01-11'}
    }

    extract = HttpResourceExtract(options=config['streams']['rate']['extract']['options'],
                                  extrapolate=extrapolate,
                                  strategy_builder=strategy_builder.build)

    extracted_result = extract.extract(context)
    logging.debug(extracted_result)

    # source = Source()
    #
    # for stream in source:
    #     for record, state in stream:
    #         emit_record(stream, record)
    #         emit_state(stream, state)
    #
    # cleanup()

if __name__ == "__main__":
    logging.info(f"Starting Magibyte {sys.argv}")
    main()
