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
import os
import sys

import yaml

from magibyte.core import strategy_builder
from magibyte.core.extrapolation import extrapolate
from magibyte.strategies.extractor.simple_extractor import SimpleExtractor

logging.basicConfig(level=logging.DEBUG)

states = {}

config_exchange_rate = {
  'base': 'USD',
  'start_date': '2021-01-01'
}

streams_exchange_rate = yaml.safe_load('''
streams:
  rates:
    extractor:
      strategy: magibyte.strategies.extractor.SimpleExtractor
      options:
        requester:
          strategy: magibyte.strategies.requester.HttpRequest
          options:
            base_url: "https://api.exchangeratesapi.io/{{ cursor.current_datetime.format('YYYY-MM-DD') }}"
            method: get
            params:
            - name: base
              value: "{{ config.base }}"
              on_empty: skip
            decoder:
              strategy: magibyte.strategies.decoder.Json
            shaper:
              strategy: magibyte.strategies.shaper.JsonQuery
              options:
                path: "merge({date: date, base: base}, rates)"
            paginator:
              strategy: magibyte.strategies.paginator.Noop
        iterator:
          strategy: magibyte.strategies.iterator.Datetime
          options:
            start_datetime: "{{ state.date | default(config.start_date) }}"
            start_inclusive: "{{ state.date | default(true) }}"
            end_datetime: "{{ now_local() }}"
            end_inclusive: true
            step: 1d
        state:
          strategy: magibyte.strategies.state.Context
          options:
            name: date
            value: "{{ cursor.current_datetime.format('YYYY-MM-DD') }}"
''')

config_stripe = {
    "client_secret": os.environ['client_secret'],
    "account_id": os.environ['account_id'],
    "start_date": "2020-05-01T00:00:00Z"
}

streams_stripe = yaml.safe_load('''
defaults:
  requester: &default_request
    strategy: magibyte.strategies.requester.HttpRequest
    options:
      base_url: "https://api.stripe.com{{ vars.path }}"
      method: get
      params:
      - name: limit
        value: 100
      - name: starting_after
        value: "{{ page.value }}"
      headers:
      - name: Authorization
        value: "Bearer {{ config.client_secret }}"
  
  pagination: &default_pagination
    strategy: magibyte.strategies.pagination.Seek
    options:
      value: "data[0].id"
  
  decoder: &default_decoder
    strategy: magibyte.strategies.decoder.Json
    
  shaper: &default_shaper
    strategy: magibyte.strategies.shaper.JsonQuery
    options:
      path: "data"
      
  iterator: &default_iterator
    strategy: magibyte.strategies.iterator.Single

  state: &default_state
    strategy: magibyte.strategies.state.Noop
    
  extractor: &default_extract
    strategy: magibyte.strategies.extractor.HttpResource
    options:
      requester: *default_request
      decoder: *default_decoder
      shaper: *default_shaper
      iterator: *default_pagination
      state: *default_state
      
streams:
  ####
  # Core
  ####

  # balance:
  #   vars:
  #     path: /v1/balance
  #   extractor: *default_extract
  # returns an object
  
  balance_transactions:
    vars:
      path: /v1/balance_transactions
    extractor: *default_extract

  charges:
    vars:
      path: /v1/charges
    extractor: *default_extract

  customers:
    vars:
      path: /v1/customers
    extractor: *default_extract

  disputes:
    vars:
      path: /v1/disputes
    extractor: *default_extract

  events:
    vars:
      path: /v1/events
    extractor: *default_extract

  files:
    vars:
      path: /v1/files
    extractor: *default_extract

  file_links:
    vars:
      path: /v1/file_links
    extractor: *default_extract

  # /v1/mandates/mandate_1IJAmu2eZvKYlo2CccvtWfFE:
  #   vars:
  #     path: 
  #   extractor: *default_extract
  # 

  payment_intents:
    vars:
      path: /v1/payment_intents
    extractor: *default_extract

  setup_intents:
    vars:
      path: /v1/setup_intents
    extractor: *default_extract

  # /v1/setup_attempts?setup_intent:
  #   vars:
  #     path: /v1/setup_attempts
  #   extractor: *default_extract

  payouts:
    vars:
      path: /v1/payouts
    extractor: *default_extract

  products:
    vars:
      path: /v1/products
    extractor: *default_extract

  prices:
    vars:
      path: /v1/prices
    extractor: *default_extract

  refunds:
    vars:
      path: /v1/refunds
    extractor: *default_extract
  
  ####
  # Payment methods
  ####
  
  # Everything is scoped by customer

  ####
  # Checkout
  ####

  checkout_sessions:
    vars:
      path: /v1/checkout/sessions
    extractor: *default_extract

  ####
  # Billing
  ####
  
  coupons:
    vars:
      path: /v1/coupons
    extractor: *default_extract
  
  credit_notes:
    vars:
      path: /v1/credit_notes
    extractor: *default_extract
  
  # /v1/customers/cus_Iv0oJFmQcCYWsz/balance_transactions:
  #   vars:
  #     path: credit_notes
  #   extractor: *default_extract
  
  # /v1/customers/cus_Iv0oJFmQcCYWsz/tax_ids:
  #   vars:
  #     path: credit_notes
  #   extractor: *default_extract
  
  invoices:
    vars:
      path: /v1/invoices
    extractor: *default_extract
  
  invoiceitems:
    vars:
      path: /v1/invoiceitems
    extractor: *default_extract
  
  plans:
    vars:
      path: /v1/plans
    extractor: *default_extract
  
  promotion_codes:
    vars:
      path: /v1/promotion_codes
    extractor: *default_extract
  
  subscriptions:
    vars:
      path: /v1/subscriptions
    extractor: *default_extract
  
  # subscription_items:
  #   vars:
  #     path: subscriptions
  #   extractor: *default_extract
  # requires subscription= param
  
  subscription_schedules:
    vars:
      path: /v1/subscription_schedules
    extractor: *default_extract
  
  tax_rates:
    vars:
      path: /v1/tax_rates
    extractor: *default_extract
  
  # /v1/subscription_items/si_DAyhPiOTjrdfTv/usage_record_summaries:
  #   vars:
  #     path: tax_rates
  #   extractor: *default_extract

  ####
  # Connect
  ####

  accounts:
    vars:
      path: /v1/accounts
    extractor: *default_extract

  application_fees:
    vars:
      path: /v1/application_fees
    extractor: *default_extract

  # /v1/application_fees/fee_1B73DOKbnvuxQXGuhY8Aw0TN/refunds:
  #   vars:
  #     path: application_fees
  #   extractor: *default_extract

  # /v1/accounts/acct_1032D82eZvKYlo2C/capabilities:
  #   vars:
  #     path: country_specs
  #   extractor: *default_extract

  country_specs:
    vars:
      path: /v1/country_specs
    extractor: *default_extract

  # /v1/accounts/acct_1032D82eZvKYlo2C/external_accounts:
  #   vars:
  #     path: country_specs
  #   extractor: *default_extract

  # /v1/accounts/acct_1032D82eZvKYlo2C/persons:
  #   vars:
  #     path: country_specs
  #   extractor: *default_extract
    
  topups:
    vars:
      path: /v1/topups
    extractor: *default_extract

  transfers:
    vars:
      path: /v1/transfers
    extractor: *default_extract
  
  # /v1/transfers/tr_1IFzyy2eZvKYlo2CEP6HJyrb/reversals:
  #   vars:
  #     path: transfers
  #   extractor: *default_extract
  
  ####
  # Fraud
  ####
  
  radar_early_fraud_warnings:
    vars:
      path: /v1/radar/early_fraud_warnings
    extractor: *default_extract
  
  reviews:
    vars:
      path: /v1/reviews
    extractor: *default_extract
    
  radar_value_lists:
    vars:
      path: /v1/radar/value_lists
    extractor: *default_extract
  
  # /v1/radar/value_list_items?value_list:
  #   vars:
  #     path: reviews
  #   extractor: *default_extract
''')


def emit_record(stream, record):
    logging.debug(record)


def emit_state(stream, state):
    states[stream.name] = state


def cleanup():
    logging.debug(states)


def main():
    # config = config_stripe
    # streams = streams_stripe
    config = config_exchange_rate
    streams = streams_exchange_rate

    logging.debug(streams)

    for name, stream in streams['streams'].items():
        if streams == streams_stripe and name != 'customers':
            continue

        print(name)

        context = {
            'config': config,
            'state': {'date': '2021-01-11'},
            'vars': stream.get('vars', {})
        }

        extract = SimpleExtractor(options=stream['extractor']['options'],
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
