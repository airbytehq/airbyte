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

from base64 import b64encode
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Addresses,
    Carriers,
    CartRules,
    Carts,
    Categories,
    Combinations,
    Configurations,
    Contacts,
    ContentManagementSystem,
    Countries,
    Currencies,
    CustomerMessages,
    Customers,
    CustomerThreads,
    Deliveries,
    Employees,
    Groups,
    Guests,
    ImageTypes,
    Languages,
    Manufacturers,
    Messages,
    OrderCarriers,
    OrderDetails,
    OrderHistories,
    OrderInvoices,
    OrderPayments,
    Orders,
    OrderSlip,
    OrderStates,
    PriceRanges,
    ProductCustomizationFields,
    ProductFeatures,
    ProductFeatureValues,
    ProductOptions,
    ProductOptionValues,
    Products,
    ProductSuppliers,
    ShopGroups,
    Shops,
    ShopUrls,
    SpecificPriceRules,
    SpecificPrices,
    States,
    StockAvailables,
    StockMovementReasons,
    StockMovements,
    Stores,
    Suppliers,
    Tags,
    Taxes,
    TaxRuleGroups,
    TaxRules,
    TranslatedConfigurations,
    WeightRanges,
    Zones,
)


class SourcePrestaShop(AbstractSource):
    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        token = b64encode(bytes(config["access_key"] + ":", "utf-8")).decode("ascii")
        authenticator = TokenAuthenticator(token, auth_method="Basic")
        return authenticator

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = self.get_authenticator(config)
        shops = Shops(authenticator=authenticator, url=config["url"]).read_records(sync_mode=SyncMode.full_refresh)
        next(shops)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        stream_classes = [
            Addresses,
            Carriers,
            CartRules,
            Carts,
            Categories,
            Combinations,
            Configurations,
            Contacts,
            ContentManagementSystem,
            Countries,
            Currencies,
            CustomerMessages,
            CustomerThreads,
            Customers,
            Deliveries,
            Employees,
            Groups,
            Guests,
            ImageTypes,
            Languages,
            Manufacturers,
            Messages,
            OrderCarriers,
            OrderDetails,
            OrderHistories,
            OrderInvoices,
            OrderPayments,
            OrderSlip,
            OrderStates,
            Orders,
            PriceRanges,
            ProductCustomizationFields,
            ProductFeatureValues,
            ProductFeatures,
            ProductOptionValues,
            ProductOptions,
            ProductSuppliers,
            Products,
            ShopGroups,
            ShopUrls,
            Shops,
            SpecificPriceRules,
            SpecificPrices,
            States,
            StockAvailables,
            StockMovementReasons,
            StockMovements,
            Stores,
            Suppliers,
            Tags,
            TaxRuleGroups,
            TaxRules,
            Taxes,
            TranslatedConfigurations,
            WeightRanges,
            Zones,
        ]

        return [cls(authenticator=authenticator, url=config["url"]) for cls in stream_classes]
