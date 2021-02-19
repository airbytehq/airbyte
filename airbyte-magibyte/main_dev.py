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
              strategy: magibyte.strategies.shaper.JMESPath
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
  shaper: &shaper
    strategy: magibyte.strategies.shaper.JQ
    options:
      script: "{{ vars.shape or '.' }}"
   
  once_iterator: &once_iterator
    strategy: magibyte.strategies.iterator.Once

  state: &state
    strategy: magibyte.strategies.state.Noop

  decoder: &decoder
    strategy: magibyte.strategies.decoder.Json
      
  object_extractor: &object_extractor
    strategy: magibyte.strategies.extractor.DefaultExtractor
    options:
      iterator:
        strategy: magibyte.strategies.iterator.Once
      requester:
        strategy: magibyte.strategies.requester.HttpRequest
        options:
          base_url: "https://api.stripe.com{{ vars.path }}"
          method: get
          headers:
          - name: Authorization
            value: "Bearer {{ config.client_secret }}"
          paginator:
            strategy: magibyte.strategies.paginator.Noop
          decoder: *decoder
          shaper: *shaper
      state: *state

  list_extractor: &list_extractor
    strategy: magibyte.strategies.extractor.DefaultExtractor
    options:
      iterator:
        strategy: magibyte.strategies.iterator.Once
      requester:
        strategy: magibyte.strategies.requester.HttpRequest
        options:
          base_url: "https://api.stripe.com{{ vars.path }}"
          method: get
          params:
          - name: limit
            value: 100
          - name: starting_after
            value: "{{ page.value }}"
            on_empty: skip
          headers:
          - name: Authorization
            value: "Bearer {{ config.client_secret }}"
          paginator:
            strategy: magibyte.strategies.paginator.Seek
            options:
              value: "data[-1].id"
          decoder: *decoder
          shaper: *shaper
      state: *state
      
streams:
  ####
  # Core
  ####

  # balance:
  #   vars:
  #     path: /v1/balance
  #     shape: "del(.object)"
  #   extractor: *object_extractor
 
  # balance_transactions:
  #   vars:
  #     path: /v1/balance_transactions
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # charges:
  #   vars:
  #     path: /v1/charges
  #     shape: ".data[] | del(.object, .refunds)"
  #   extractor: *list_extractor
 
  # customers:
  #   vars:
  #     path: /v1/customers
  #     shape: ".data[] | del(.object, .items, .sources, .subscriptions, .tax_ids)"
  #   extractor: *list_extractor
 
  # disputes:
  #   vars:
  #     path: /v1/disputes
  #     shape: ".data[] | del(.object, .balance_transactions)"
  #   extractor: *list_extractor
 
  # # should exclude sub fields 
  # events:
  #   vars:
  #     path: /v1/events
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # files:
  #   vars:
  #     path: /v1/files
  #     shape: ".data[] | del(.object, .links)"
  #   extractor: *list_extractor
 
  # file_links:
  #   vars:
  #     path: /v1/file_links
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # # /v1/mandates/mandate_1IJAmu2eZvKYlo2CccvtWfFE:
  # #   vars:
  # #     path: 
  # #   extractor: *default_extract
 
  # payment_intents:
  #   vars:
  #     path: /v1/payment_intents
  #     shape: ".data[] | del(.object, .charges)"
  #   extractor: *list_extractor
 
  # setup_intents:
  #   vars:
  #     path: /v1/setup_intents
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # # /v1/setup_attempts?setup_intent:
  # #   vars:
  # #     path: /v1/setup_attempts
  # #   extractor: *default_extract
 
  # payouts:
  #   vars:
  #     path: /v1/payouts
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # products:
  #   vars:
  #     path: /v1/products
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # prices:
  #   vars:
  #     path: /v1/prices
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # refunds:
  #   vars:
  #     path: /v1/refunds
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  ####
  # Payment methods
  ####
 
  # Everything is scoped by customer
 
  ####
  # Checkout
  ####

  # checkout_sessions:
  #   vars:
  #     path: /v1/checkout/sessions
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  ####
  # Billing
  ####

  # coupons:
  #   vars:
  #     path: /v1/coupons
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # credit_notes:
  #   vars:
  #     path: /v1/credit_notes
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # # /v1/customers/cus_Iv0oJFmQcCYWsz/balance_transactions:
  # #   vars:
  # #     path: credit_notes
  # #   extractor: *default_extract

  # # /v1/customers/cus_Iv0oJFmQcCYWsz/tax_ids:
  # #   vars:
  # #     path: credit_notes
  # #   extractor: *default_extract

  # invoices:
  #   vars:
  #     path: /v1/invoices
  #     shape: ".data[] | del(.object, .lines)"
  #   extractor: *list_extractor
 
  # invoiceitems:
  #   vars:
  #     path: /v1/invoiceitems
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # plans:
  #   vars:
  #     path: /v1/plans
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # promotion_codes:
  #   vars:
  #     path: /v1/promotion_codes
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # subscriptions:
  #   vars:
  #     path: /v1/subscriptions
  #     shape: ".data[] | del(.object, .items)"
  #   extractor: *list_extractor

  # # subscription_items:
  # #   vars:
  # #     path: subscriptions
  # #   extractor: *default_extract
  # # requires subscription= param

  # subscription_schedules:
  #   vars:
  #     path: /v1/subscription_schedules
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # tax_rates:
  #   vars:
  #     path: /v1/tax_rates
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # # /v1/subscription_items/si_DAyhPiOTjrdfTv/usage_record_summaries:
  # #   vars:
  # #     path: tax_rates
  # #   extractor: *default_extract
 
  ####
  # Connect
  ####
 
  # accounts:
  #   vars:
  #     path: /v1/accounts
  #     shape: ".data[] | del(.object, .external_accounts)"
  #   extractor: *list_extractor
 
  # application_fees:
  #   vars:
  #     path: /v1/application_fees
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
    
  # # /v1/application_fees/fee_1B73DOKbnvuxQXGuhY8Aw0TN/refunds:
  # #   vars:
  # #     path: application_fees
  # #   extractor: *default_extract

  # # /v1/accounts/acct_1032D82eZvKYlo2C/capabilities:
  # #   vars:
  # #     path: country_specs
  # #   extractor: *default_extract
 
  # country_specs:
  #   vars:
  #     path: /v1/country_specs
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor

  # # /v1/accounts/acct_1032D82eZvKYlo2C/external_accounts:
  # #   vars:
  # #     path: country_specs
  # #   extractor: *default_extract

  # # /v1/accounts/acct_1032D82eZvKYlo2C/persons:
  # #   vars:
  # #     path: country_specs
  # #   extractor: *default_extract
   
  # topups:
  #   vars:
  #     path: /v1/topups
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # transfers:
  #   vars:
  #     path: /v1/transfers
  #     shape: ".data[] | del(.object, .reversals)"
  #   extractor: *list_extractor

  # # /v1/transfers/tr_1IFzyy2eZvKYlo2CEP6HJyrb/reversals:
  # #   vars:
  # #     path: transfers
  # #   extractor: *default_extract

  # ####
  # # Fraud
  # ####

  # radar_early_fraud_warnings:
  #   vars:
  #     path: /v1/radar/early_fraud_warnings
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
 
  # reviews:
  #   vars:
  #     path: /v1/reviews
  #     shape: ".data[] | del(.object)"
  #   extractor: *list_extractor
   
  # radar_value_lists:
  #   vars:
  #     path: /v1/radar/value_lists
  #     shape: ".data[] | del(.object, .list_items)"
  #   extractor: *list_extractor

  # # /v1/radar/value_list_items?value_list:
  # #   vars:
  # #     path: reviews
  # #   extractor: *default_extract
''')


def emit_record(stream, record):
    logging.debug(record)


def emit_state(stream, state):
    states[stream.name] = state


def cleanup():
    logging.debug(states)


def main():
    config = config_stripe
    streams = streams_stripe
    # config = config_exchange_rate
    # streams = streams_exchange_rate

    logging.debug(streams)

    for name, stream in streams['streams'].items():
        # if streams == streams_stripe and name not in ('balance', ):
        #     continue

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
