#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type, Union

import pydantic
import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.utils.schema_helpers import expand_refs
from braintree.attribute_getter import AttributeGetter
from braintree.customer import Customer as BCustomer
from braintree.discount import Discount as BDiscount
from braintree.dispute import Dispute as BDispute
from braintree.merchant_account.merchant_account import MerchantAccount as BMerchantAccount
from braintree.plan import Plan as BPlan
from braintree.subscription import Subscription as BSubscription
from braintree.transaction import Transaction as BTransaction
from braintree.util.xml_util import XmlUtil
from pydantic import BaseModel
from pydantic.typing import resolve_annotations

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


@dataclass
class BraintreeExtractor(RecordExtractor):
    """
    Extractor Template for all BrainTree streams.
    """

    @staticmethod
    def _extract_as_array(results, attribute):
        if attribute not in results:
            return []

        value = results[attribute]
        if not isinstance(value, list):
            value = [value]
        return value

    def _get_json_from_resource(self, resource_obj: Union[AttributeGetter, List[AttributeGetter]]):
        if isinstance(resource_obj, list):
            return [obj if not isinstance(obj, AttributeGetter) else self._get_json_from_resource(obj) for obj in resource_obj]
        obj_dict = resource_obj.__dict__
        result = dict()
        for attr in obj_dict:
            if not attr.startswith("_"):
                if callable(obj_dict[attr]):
                    continue
                result[attr] = (
                    self._get_json_from_resource(obj_dict[attr]) if isinstance(obj_dict[attr], (AttributeGetter, list)) else obj_dict[attr]
                )
        return result


@dataclass
class MerchantAccountExtractor(BraintreeExtractor):
    """
    Extractor for Merchant Accounts stream.
    It parses output XML and finds all `Merchant Account` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)["merchant_accounts"]
        merchant_accounts = self._extract_as_array(data, "merchant_account")
        return [
            MerchantAccount(**self._get_json_from_resource(BMerchantAccount(None, merchant_account))).dict(exclude_unset=True)
            for merchant_account in merchant_accounts
        ]


@dataclass
class CustomerExtractor(BraintreeExtractor):
    """
    Extractor for Customers stream.
    It parses output XML and finds all `Customer` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)["customers"]
        customers = self._extract_as_array(data, "customer")
        return [Customer(**self._get_json_from_resource(BCustomer(None, customer))).dict(exclude_unset=True) for customer in customers]


@dataclass
class DiscountExtractor(BraintreeExtractor):
    """
    Extractor for Discounts stream.
    It parses output XML and finds all `Discount` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)
        discounts = self._extract_as_array(data, "discounts")
        return [Discount(**self._get_json_from_resource(BDiscount(None, discount))).dict(exclude_unset=True) for discount in discounts]


@dataclass
class TransactionExtractor(BraintreeExtractor):
    """
    Extractor for Transactions stream.
    It parses output XML and finds all `Transaction` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)["credit_card_transactions"]
        transactions = self._extract_as_array(data, "transaction")
        return [
            Transaction(**self._get_json_from_resource(BTransaction(None, transaction))).dict(exclude_unset=True)
            for transaction in transactions
        ]


@dataclass
class SubscriptionExtractor(BraintreeExtractor):
    """
    Extractor for Subscriptions stream.
    It parses output XML and finds all `Subscription` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)["subscriptions"]
        subscriptions = self._extract_as_array(data, "subscription")
        return [
            Subscription(**self._get_json_from_resource(BSubscription(None, subscription))).dict(exclude_unset=True)
            for subscription in subscriptions
        ]


@dataclass
class PlanExtractor(BraintreeExtractor):
    """
    Extractor for Plans stream.
    It parses output XML and finds all `Plan` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)
        plans = self._extract_as_array(data, "plans")
        return [Plan(**self._get_json_from_resource(BPlan(None, plan))).dict(exclude_unset=True) for plan in plans]


@dataclass
class DisputeExtractor(BraintreeExtractor):
    """
    Extractor for Disputes stream.
    It parses output XML and finds all `Dispute` occurrences in it.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> List[Record]:
        data = XmlUtil.dict_from_xml(response.text)["disputes"]
        disputes = self._extract_as_array(data, "dispute")
        return [Dispute(**self._get_json_from_resource(BDispute(dispute))).dict(exclude_unset=True) for dispute in disputes]


class AllOptional(pydantic.main.ModelMetaclass):
    """
    Metaclass for marking all Pydantic model fields as Optional
    Here is exmaple of declaring model using this metaclasslike:
    '''
            class MyModel(BaseModel, metaclass=AllOptional):
                a: str
                b: str
    '''
    Its equivalent of:
    '''
            class MyModel(BaseModel):
                a: Optional[str]
                b: Optional[str]
    '''
    It would make code more clear and eliminate a lot of manual work.
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        """
        Iterate through fields and wrap then with typing.Optional type.
        """
        annotations = resolve_annotations(namespaces.get("__annotations__", {}), namespaces.get("__module__", None))
        for base in bases:
            annotations = {**annotations, **getattr(base, "__annotations__", {})}
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class CatalogModel(BaseModel, metaclass=AllOptional):
    class Config:
        arbitrary_types_allowed = True

        @classmethod
        def schema_extra(cls, schema: Dict[str, Any], model: Type["BaseModel"]) -> None:
            schema.pop("title", None)
            schema.pop("description", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                prop.pop("description", None)
                allow_none = model.__fields__[name].allow_none
                if allow_none:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]

    @classmethod
    def schema(cls, **kwargs) -> Dict[str, Any]:
        schema = super().schema(**kwargs)
        expand_refs(schema)
        return schema


class Address(CatalogModel):
    company: str
    country_code_alpha2: str
    country_code_alpha3: str
    country_code_numeric: str
    country_name: str
    created_at: datetime
    customer_id: str
    extended_address: str
    first_name: str
    id: str
    last_name: str
    locality: str
    postal_code: str
    region: str
    street_address: str
    updated_at: datetime


class CreditCard(CatalogModel):
    """
    https://developer.paypal.com/braintree/docs/reference/response/credit-card
    """

    billing_address: Address
    bin: str
    card_type: str
    cardholder_name: str
    commercial: str
    country_of_issuance: str
    created_at: datetime
    customer_id: str
    customer_location: str
    debit: str
    default: bool
    durbin_regulated: str
    expiration_date: str
    expiration_month: str
    expiration_year: str
    expired: bool
    healthcare: str
    image_url: str
    issuing_bank: str
    last_4: str
    masked_number: str
    payroll: str
    prepaid: str
    product_id: str
    token: str
    unique_number_identifier: str
    updated_at: datetime


class ApplePayCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/apple-pay-card
    """

    source_description: str
    payment_instrument_name: str


class SamsungPayCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/samsung-pay-card
    """


class MasterpassCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/masterpass-card
    """


class AndroidPayCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/android-pay-card
    """

    google_transaction_id: str
    source_card_type: str
    source_description: str
    is_network_tokenized: bool
    source_card_last_4: str
    source_card_type: str
    virtual_card_last_4: str
    virtual_card_type: str


class VisaCheckoutCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/visa-checkout-card
    """


class VenmoAccount(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/venmo-account
    """

    source_description: str
    username: str
    venmo_user_id: str


class PayPalAccount(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/paypal-account
    """

    billing_agreement_id: str
    email: str
    payer_id: str
    revoked_at: datetime


class USBankAccount(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/us-bank-account
    """

    account_holder_name: str
    account_type: str
    ach_mandate: str
    bank_name: str
    business_name: str
    last_name: str
    owner_id: str
    ownership_type: str
    plaid_verified_at: datetime
    routing_number: str
    verifiable: bool
    verified: bool


PaymentMethod = Union[
    CreditCard, AndroidPayCard, ApplePayCard, SamsungPayCard, USBankAccount, PayPalAccount, VenmoAccount, VisaCheckoutCard
]


class AddOn(CatalogModel):
    amount: Decimal
    current_billing_cycle: Optional[Decimal]
    description: str
    id: str
    kind: str
    name: str
    never_expires: bool
    number_of_billing_cycles: Optional[Decimal]
    quantity: Optional[Decimal]


class Customer(CatalogModel):
    addresses: List[Address]
    android_pay_cards: Optional[List[AndroidPayCard]]
    apple_pay_cards: Optional[List[ApplePayCard]]
    company: str
    created_at: datetime
    credit_cards: Optional[List[CreditCard]]
    custom_fields: str
    email: str
    fax: str
    first_name: str
    graphql_id: str
    id: str
    last_name: str
    masterpass_cards: List[MasterpassCard]
    payment_methods: List[PaymentMethod]
    paypal_accounts: List[PayPalAccount]
    phone: str
    samsung_pay_cards: List[SamsungPayCard]
    updated_at: datetime
    us_bank_accounts: List[USBankAccount]
    venmo_accounts: List[VenmoAccount]
    visa_checkout_cards: List[VisaCheckoutCard]
    website: str


class Discount(CatalogModel):
    amount: Decimal
    current_billing_cycle: Optional[Decimal]
    description: str
    id: str
    kind: str
    name: str
    never_expires: bool
    number_of_billing_cycles: Optional[Decimal]
    quantity: Optional[Decimal]


class Evidence(CatalogModel, metaclass=AllOptional):
    created_at: datetime
    id: str
    sent_to_processor_at: datetime
    url: str
    comment: str


class PaypalMessage(CatalogModel):
    message: str
    send_at: datetime
    sender: str


class Dispute(CatalogModel):
    amount_disputed: Decimal
    amount_won: Decimal
    case_number: str
    chargeback_protection_level: Optional[str]
    created_at: datetime
    currency_iso_code: str
    evidence: Union[Evidence, List[Evidence]]
    graphql_id: str
    id: str
    kind: str
    merchant_account_id: str
    original_dispute_id: Optional[str]
    paypal_messages: List[PaypalMessage]
    processor_comments: Optional[str]
    reason: str
    reason_code: str
    reason_description: Optional[str]
    received_date: date
    reference_number: Optional[str]
    reply_by_date: date
    status: str
    updated_at: datetime


class BussinessDetails(CatalogModel):
    address_details: Address
    dba_name: str
    legal_name: str
    tax_id: str


class FundingDetails(CatalogModel):
    account_number_last_4: str
    descriptor: str
    destination: str
    email: str
    mobile_phone: str
    routing_number: str


class IndividualDetails(CatalogModel):
    address_details: Address
    date_of_birth: str
    email: str
    first_name: str
    last_name: str
    phone: str
    ssn_last_4: str


class MerchantAccount(CatalogModel):
    business_details: BussinessDetails
    currency_iso_code: str
    funding_details: FundingDetails
    id: str
    individual_details: IndividualDetails
    status: str


class Plan(CatalogModel):
    add_ons: List[AddOn]
    billing_day_of_month: Optional[Decimal]
    billing_frequency: Decimal
    created_at: datetime
    currency_iso_code: str
    description: str
    discounts: List[Discount]
    id: str
    name: str
    number_of_billing_cycles: Optional[Decimal]
    price: Decimal
    trial_duration: Decimal
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime


class DisbursementDetails(BaseModel):
    disbursement_date: date
    funds_held: bool
    settlement_amount: Decimal
    settlement_base_currency_exchange_rate: Decimal
    settlement_currency_exchange_rate: Decimal
    settlement_currency_iso_code: str
    success: bool


class StatusHistoryDetails(BaseModel):
    amount: Decimal
    status: str
    timestamp: datetime
    transaction_source: str
    user: Optional[str]


class SubscriptionDetails(BaseModel):
    billing_period_end_date: Optional[date]
    billing_period_start_date: Optional[date]


class Transaction(BaseModel):
    acquirer_reference_number: str
    additional_processor_response: str
    amount: str
    android_pay_card_details: AndroidPayCard
    apple_pay_details: ApplePayCard
    authorization_expires_at: datetime
    avs_error_response_code: str
    avs_postal_code_response_code: str
    avs_street_address_response_code: str
    billing_details: Address
    channel: str
    created_at: datetime
    credit_card_details: CreditCard
    currency_iso_code: str
    custom_fields: Dict[str, str]
    customer_details: Customer
    cvv_response_code: str
    disbursement_details: DisbursementDetails
    discount_amount: Decimal
    discounts: List[Discount]
    disputes: List[Dispute]
    escrow_status: str
    gateway_rejection_reason: str
    global_id: str
    graphql_id: str
    id: str
    installment_count: Decimal
    masterpass_card_details: MasterpassCard
    merchant_account_id: str
    merchant_address: Address
    merchant_identification_number: str
    merchant_name: str
    network_response_code: str
    network_response_text: str
    network_transaction_id: str
    order_id: str
    payment_instrument_type: str
    pin_verified: bool
    plan_id: str
    processed_with_network_token: bool
    processor_authorization_code: str
    processor_response_code: str
    processor_response_text: str
    processor_response_type: str
    processor_settlement_response_code: str
    processor_settlement_response_text: str
    purchase_order_number: str
    paypal_details: PayPalAccount
    recurring: bool
    refund_ids: List[str]
    refund_global_ids: List[str]
    refunded_transaction_id: str
    response_emv_data: str
    retrieval_reference_number: str
    samsung_pay_card_details: SamsungPayCard
    sca_exemption_requested: str
    service_fee_amount: Decimal
    settlement_batch_id: str
    shipping_amount: Decimal
    shipping_details: Address
    ships_from_postal_code: str
    status: str
    status_history: List[StatusHistoryDetails]
    subscription_details: SubscriptionDetails
    subscription_id: str
    tax_amount: Decimal
    tax_exempt: bool
    terminal_identification_number: str
    type: str
    updated_at: datetime
    venmo_account_details: VenmoAccount
    visa_checkout_card_details: VisaCheckoutCard
    voice_referral_number: str


class Subscription(CatalogModel):
    add_ons: List[AddOn]
    balance: Decimal
    billing_day_of_month: Decimal
    billing_period_start_date: date
    billing_period_end_date: date
    created_at: datetime
    current_billing_cycle: Decimal
    days_past_due: Decimal
    description: str
    discounts: List[Discount]
    failure_count: Decimal
    first_billing_date: date
    id: str
    merchant_account_id: str
    never_expires: bool
    next_bill_amount: Decimal
    next_billing_date: date
    next_billing_period_amount: Decimal
    number_of_billing_cycles: Decimal
    paid_through_date: date
    payment_method_token: str
    plan_id: str
    price: Decimal
    status: str
    transactions: List[Transaction]
    trial_duration: Decimal
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime
