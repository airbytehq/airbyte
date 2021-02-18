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
from magibyte.strategies.extract.http_resource_extract import HttpResourceExtract

logging.basicConfig(level=logging.DEBUG)

states = {}

config_exchange_rate = yaml.safe_load('''
config:
  base: USD
  start_date: 2021-01-01
''')

streams_exchange_rate = yaml.safe_load('''
streams:
  rates:
    extract:
      strategy: magibyte.strategies.extract.HttpResource
      options:
        request:
          strategy: magibyte.strategies.request.HttpRequest
          options:
            base_url: "https://api.exchangeratesapi.io/{{ page.current_datetime.format('YYYY-MM-DD') }}"
            method: get
            params:
            - name: base
              value: "{{ config.base }}"
        decoder:
          strategy: magibyte.strategies.decoder.Json
        shaper:
          strategy: magibyte.strategies.shaper.JsonQuery
          options:
            path: "merge({date: date, base: base}, rates)"
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
            value: "{{ page.current_datetime.format('YYYY-MM-DD') }}"
''')

config_stripe = {
    "client_secret": os.environ['client_secret'],
    "account_id": os.environ['account_id'],
    "start_date": "2020-05-01T00:00:00Z"
}

streams_stripe = yaml.safe_load('''
defaults:
  request: &default_request
    strategy: magibyte.strategies.request.HttpRequest
    options:
      base_url: "https://api.stripe.com{{ vars.path }}"
      method: get
      params: []
      headers:
      - name: Authorization
        value: "Bearer {{ config.client_secret }}"
  
  decoder: &default_decoder
    strategy: magibyte.strategies.decoder.Json
    
  shaper: &default_shaper
    strategy: magibyte.strategies.shaper.JsonQuery
    options:
      path: "data"
      
  iterator: &default_pagination
    strategy: magibyte.strategies.iterator.Single

  state: &default_state
    strategy: magibyte.strategies.state.Noop
    
  extract: &default_extract
    strategy: magibyte.strategies.extract.HttpResource
    options:
      request: *default_request
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
  #   extract: *default_extract
  # returns an object
  
  balance_transactions:
    vars:
      path: /v1/balance_transactions
    extract: *default_extract

  charges:
    vars:
      path: /v1/charges
    extract: *default_extract

  customers:
    vars:
      path: /v1/customers
    extract: *default_extract

  disputes:
    vars:
      path: /v1/disputes
    extract: *default_extract

  events:
    vars:
      path: /v1/events
    extract: *default_extract

  files:
    vars:
      path: /v1/files
    extract: *default_extract

  file_links:
    vars:
      path: /v1/file_links
    extract: *default_extract

  # /v1/mandates/mandate_1IJAmu2eZvKYlo2CccvtWfFE:
  #   vars:
  #     path: 
  #   extract: *default_extract
  # 

  payment_intents:
    vars:
      path: /v1/payment_intents
    extract: *default_extract

  setup_intents:
    vars:
      path: /v1/setup_intents
    extract: *default_extract

  # /v1/setup_attempts?setup_intent:
  #   vars:
  #     path: /v1/setup_attempts
  #   extract: *default_extract

  payouts:
    vars:
      path: /v1/payouts
    extract: *default_extract

  products:
    vars:
      path: /v1/products
    extract: *default_extract

  prices:
    vars:
      path: /v1/prices
    extract: *default_extract

  refunds:
    vars:
      path: /v1/refunds
    extract: *default_extract
  
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
    extract: *default_extract

  ####
  # Billing
  ####
  
  coupons:
    vars:
      path: /v1/coupons
    extract: *default_extract
  
  credit_notes:
    vars:
      path: /v1/credit_notes
    extract: *default_extract
  
  # /v1/customers/cus_Iv0oJFmQcCYWsz/balance_transactions:
  #   vars:
  #     path: credit_notes
  #   extract: *default_extract
  
  # /v1/customers/cus_Iv0oJFmQcCYWsz/tax_ids:
  #   vars:
  #     path: credit_notes
  #   extract: *default_extract
  
  invoices:
    vars:
      path: /v1/invoices
    extract: *default_extract
  
  invoiceitems:
    vars:
      path: /v1/invoiceitems
    extract: *default_extract
  
  plans:
    vars:
      path: /v1/plans
    extract: *default_extract
  
  promotion_codes:
    vars:
      path: /v1/promotion_codes
    extract: *default_extract
  
  subscriptions:
    vars:
      path: /v1/subscriptions
    extract: *default_extract
  
  # subscription_items:
  #   vars:
  #     path: subscriptions
  #   extract: *default_extract
  # requires subscription= param
  
  subscription_schedules:
    vars:
      path: /v1/subscription_schedules
    extract: *default_extract
  
  tax_rates:
    vars:
      path: /v1/tax_rates
    extract: *default_extract
  
  # /v1/subscription_items/si_DAyhPiOTjrdfTv/usage_record_summaries:
  #   vars:
  #     path: tax_rates
  #   extract: *default_extract

  ####
  # Connect
  ####

  accounts:
    vars:
      path: /v1/accounts
    extract: *default_extract

  application_fees:
    vars:
      path: /v1/application_fees
    extract: *default_extract

  # /v1/application_fees/fee_1B73DOKbnvuxQXGuhY8Aw0TN/refunds:
  #   vars:
  #     path: application_fees
  #   extract: *default_extract

  # /v1/accounts/acct_1032D82eZvKYlo2C/capabilities:
  #   vars:
  #     path: country_specs
  #   extract: *default_extract

  country_specs:
    vars:
      path: /v1/country_specs
    extract: *default_extract

  # /v1/accounts/acct_1032D82eZvKYlo2C/external_accounts:
  #   vars:
  #     path: country_specs
  #   extract: *default_extract

  # /v1/accounts/acct_1032D82eZvKYlo2C/persons:
  #   vars:
  #     path: country_specs
  #   extract: *default_extract
    
  topups:
    vars:
      path: /v1/topups
    extract: *default_extract

  transfers:
    vars:
      path: /v1/transfers
    extract: *default_extract
  
  # /v1/transfers/tr_1IFzyy2eZvKYlo2CEP6HJyrb/reversals:
  #   vars:
  #     path: transfers
  #   extract: *default_extract
  
  ####
  # Fraud
  ####
  
  radar_early_fraud_warnings:
    vars:
      path: /v1/radar/early_fraud_warnings
    extract: *default_extract
  
  reviews:
    vars:
      path: /v1/reviews
    extract: *default_extract
    
  radar_value_lists:
    vars:
      path: /v1/radar/value_lists
    extract: *default_extract
  
  # /v1/radar/value_list_items?value_list:
  #   vars:
  #     path: reviews
  #   extract: *default_extract
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
        # if name != 'customers':
        #     continue

        print(name)

        context = {
            'config': config,
            'state': {'date': '2021-01-11'},
            'vars': stream.get('vars', {})
        }

        extract = HttpResourceExtract(options=stream['extract']['options'],
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
