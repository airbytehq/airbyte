#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
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
    def _validate_and_transform(self, config: Mapping[str, Any]):
        if not config.get("_allow_http"):
            if re.match(r"^http://", config["url"], re.I):
                raise Exception(f"Invalid url: {config['url']}, only https scheme is allowed")
        return config

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        token = b64encode(bytes(config["access_key"] + ":", "utf-8")).decode("ascii")
        authenticator = TokenAuthenticator(token, auth_method="Basic")
        return authenticator

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = self._validate_and_transform(config)
        authenticator = self.get_authenticator(config)
        shops = Shops(authenticator=authenticator, url=config["url"]).read_records(sync_mode=SyncMode.full_refresh)
        next(shops)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
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
