#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from pytest import fixture
from source_pagarme.source import SourcePagarme


@fixture
def test_config():
    return {"api_key": "key", "start_date": "2022-10-19T20:00:00.000Z"}


def setup_responses():
    responses.add(
        responses.GET,
        "https://api.pagar.me/1/transactions?count=1000",
        json={
            "object": "transaction",
            "status": "paid",
            "refuse_reason": None,
            "status_reason": "acquirer",
            "acquirer_response_code": "0000",
            "acquirer_response_message": "Transação aprovada com sucesso",
            "acquirer_name": "pagarme",
            "acquirer_id": "54cfc899eb655fe03300000b",
            "authorization_code": "00000",
            "soft_descriptor": None,
            "tid": 938402850,
            "nsu": 938402850,
            "date_created": "2022-10-28T18:25:09.103Z",
            "date_updated": "2022-10-28T18:25:10.195Z",
            "amount": 2900,
            "authorized_amount": 2900,
            "paid_amount": 2900,
            "refunded_amount": 0,
            "installments": 1,
            "id": 938402850,
            "cost": 30,
            "card_holder_name": "Name",
            "card_last_digits": "1111",
            "card_first_digits": "2222",
            "card_brand": "branb",
            "card_pin_mode": None,
            "card_magstripe_fallback": False,
            "cvm_pin": False,
            "postback_url": None,
            "payment_method": "credit_card",
            "capture_method": "ecommerce",
            "antifraud_score": None,
            "boleto_url": None,
            "boleto_barcode": None,
            "boleto_expiration_date": None,
            "boleto": None,
            "referer": "api_key",
            "ip": "ip",
            "subscription_id": 1111111,
            "phone": None,
            "address": None,
            "customer": {
                "object": "customer",
                "id": 1,
                "external_id": None,
                "type": None,
                "country": None,
                "document_number": None,
                "document_type": "cpf",
                "name": "Name",
                "email": "name@mail.com",
                "phone_numbers": None,
                "born_at": None,
                "birthday": None,
                "gender": None,
                "date_created": "2021-10-09T00:34:45.080Z",
                "documents": [],
                "client_since": None,
                "risk_indicator": None
            },
            "billing": None,
            "shipping": None,
            "items": [],
            "card": {
                "object": "card",
                "id": "card_xxxxxxxxxxxxxxxxx",
                "date_created": "2022-10-28T18:25:09.094Z",
                "date_updated": "2022-10-28T18:25:10.228Z",
                "brand": "mastercard",
                "holder_name": "Name",
                "first_digits": "1111",
                "last_digits": "22222",
                "country": "country",
                "fingerprint": "fingerprint",
                "valid": True,
                "expiration_date": "8908"
            },
            "split_rules": None,
            "antifraud_metadata": {},
            "reference_key": None,
            "device": None,
            "local_transaction_id": None,
            "local_time": None,
            "fraud_covered": False,
            "fraud_reimbursed": None,
            "order_id": None,
            "risk_level": "unknown",
            "receipt_url": None,
            "payment": None,
            "addition": None,
            "discount": None,
            "private_label": None,
            "pix_data": None,
            "pix_qr_code": None,
            "pix_expiration_date": None,
            "metadata": {
                "productName": "Product",
                "clientId": "1",
                "productId": "111",
                "utm_campaign": "utm_campaign",
                "productType": "subscription",
                "orderCode": "111111111111"
            }
        }
    )


@responses.activate
def test_check_connection(test_config):
    setup_responses()
    source = SourcePagarme()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


def test_streams(mocker):
    source = SourcePagarme()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 13
    assert len(streams) == expected_streams_number
