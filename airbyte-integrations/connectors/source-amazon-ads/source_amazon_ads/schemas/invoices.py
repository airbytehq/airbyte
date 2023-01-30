#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import List, Dict

from .common import CatalogModel


class CurrencyAmount(CatalogModel):
    amount: Decimal
    currencyCode: str


class FeeIdentifiers(CatalogModel):
    countryCode: str


class Fee(CatalogModel):
    cost: CurrencyAmount
    feeIdentifiers: FeeIdentifiers
    feeType: str


class InvoiceSummary(CatalogModel):
    fees: List[Fee]
    paymentTermsDays: int
    taxAmountDue: CurrencyAmount
    remainingTaxAmountDue: CurrencyAmount
    remainingFees: List[Fee]
    toDate: str
    dueDate: str
    invoiceDate: str
    remainingAmountDue: CurrencyAmount
    fromDate: str
    amountDue: CurrencyAmount
    taxRate: Decimal
    purchaseOrderNumber: str
    paymentMethod: str
    id: str
    downloadableDocuments: List[str]
    status: str


class InvoicesPayload(CatalogModel):
    nextCursor: str
    previousCursor: str
    invoiceSummaries: List[InvoiceSummary]


class InvoicesResponse(CatalogModel):
    status: str
    payload: InvoicesPayload


class Promotion(CatalogModel):
    lastConsumedDate: str
    amount: CurrencyAmount
    description: str


class GovernmentInvoiceInformation(CatalogModel):
    transactionType: str
    countryCode: str
    governmentInvoiceId: str


class Address(CatalogModel):
    stateOrRegion: str
    attentionName: str
    city: str
    countryCode: str
    companyName: str
    postalCode: str
    addressLine1: str
    addressLine2: str
    addressLine3: str


class Email(CatalogModel):
    emailAddress: str
    displayName: str


class ContactInfo(CatalogModel):
    address: Address
    email: Email


class TaxRegistrationInfo(CatalogModel):
    taxId: str


class TaxBreakup(CatalogModel):
    payerJurisdiction: str
    taxRate: Decimal
    issuerTaxInformation: TaxRegistrationInfo
    thirdPartyTaxInformation: TaxRegistrationInfo
    issuerJurisdiction: str
    payerTaxInformation: TaxRegistrationInfo
    taxAmount: CurrencyAmount
    taxName: str
    taxedJurisdictionName: str


class TaxDetail(CatalogModel):
    permanentAccountNumber: str
    taxCalculationDate: str
    taxBreakups: List[TaxBreakup]


class Adjustment(CatalogModel):
    amount: CurrencyAmount
    accountingDate: str
    fees: List[Fee]
    comments: str
    portfolioId: int


class InvoiceLine(CatalogModel):
    campaignTags: Dict[str, str]
    costEventType: str
    commissionRate: Decimal
    fees: List[Fee]
    cost: CurrencyAmount
    campaignId: int
    priceType: str
    supplyCost: CurrencyAmount
    portfolioId: int
    costPerEventType: Decimal
    programName: str
    costEventCount: int
    purchaseOrderNumber: str
    purchaseOrderNumber: str
    campaignName: str
    promotionAmount: CurrencyAmount
    costPerUnit: Decimal
    commissionAmount: CurrencyAmount


class Payment(CatalogModel):
    nextPaymentAttemptDate: str
    reason: str
    amount: CurrencyAmount
    paymentMethod: str
    currentPaymentAttemptDate: str
    id: int
    lastPaymentAttemptDate: str
    refundedAmount: CurrencyAmount
    status: str


class Portfolio(CatalogModel):
    totalAmount: CurrencyAmount
    feeAmount: CurrencyAmount
    name: str
    id: int


class InvoicePayload(CatalogModel):
    promotions: List[Promotion]
    governmentInvoiceInformation: GovernmentInvoiceInformation
    payerContactInfo: ContactInfo
    taxDetail: TaxDetail
    adjustments: List[Adjustment]
    invoiceLines: List[InvoiceLine]
    invoiceSummary: InvoiceSummary
    issuerContactInfo: ContactInfo
    thirdPartyContactInfo: ContactInfo
    payments: List[Payment]
    portfolios: List[Portfolio]


class InvoiceResponse(CatalogModel):
    status: str
    payload: InvoicePayload
