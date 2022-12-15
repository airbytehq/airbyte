#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from .cards import (
    Address,
    AndroidPayCard,
    ApplePayCard,
    CreditCard,
    MasterpassCard,
    PayPalAccount,
    SamsungPayCard,
    VenmoAccount,
    VisaCheckoutCard,
)
from .common import CatalogModel as BaseModel
from .customer import Customer
from .discount import Discount
from .dispute import Dispute


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
    billing_period_end_date: Optional[datetime]
    billing_period_start_date: Optional[datetime]


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
    custom_fields: str
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
