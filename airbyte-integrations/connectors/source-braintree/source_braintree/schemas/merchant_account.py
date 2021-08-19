#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
