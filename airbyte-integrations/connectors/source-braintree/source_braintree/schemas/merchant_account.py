#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from .cards import Address
from .common import CatalogModel


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
