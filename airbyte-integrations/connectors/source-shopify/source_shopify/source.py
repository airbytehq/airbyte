#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException
from requests.exceptions import ConnectionError, RequestException, SSLError

from .auth import MissingAccessTokenError, ShopifyAuthenticator
from .scopes import ShopifyScopes
from .streams.streams import (
    AbandonedCheckouts,
    Articles,
    BalanceTransactions,
    Blogs,
    Collections,
    Collects,
    Countries,
    CustomCollections,
    CustomerAddress,
    CustomerJourneySummary,
    Customers,
    CustomerSavedSearch,
    DiscountCodes,
    Disputes,
    DraftOrders,
    FulfillmentOrders,
    Fulfillments,
    InventoryItems,
    InventoryLevels,
    Locations,
    MetafieldArticles,
    MetafieldBlogs,
    MetafieldCollections,
    MetafieldCustomers,
    MetafieldDraftOrders,
    MetafieldLocations,
    MetafieldOrders,
    MetafieldPages,
    MetafieldProductImages,
    MetafieldProducts,
    MetafieldProductVariants,
    MetafieldShops,
    MetafieldSmartCollections,
    OrderRefunds,
    OrderRisks,
    Orders,
    Pages,
    PriceRules,
    ProductImages,
    Products,
    ProductsGraphQl,
    ProductVariants,
    Shop,
    SmartCollections,
    TenderTransactions,
    Transactions,
    TransactionsGraphql,
)


class ConnectionCheckTest:
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        # use `Shop` as a test stream for connection check
        self.test_stream = Shop(self.config)
        # setting `max_retries` to 0 for the stage of `check connection`,
        # because it keeps retrying for wrong shop names,
        # but it should stop immediately
        self.test_stream.max_retries = 0

    def describe_error(self, pattern: str, shop_name: str = None, details: Any = None, **kwargs) -> str:
        connection_check_errors_map: Mapping[str, Any] = {
            "connection_error": f"Connection could not be established using `Shopify Store`: {shop_name}. Make sure it's valid and try again.",
            "request_exception": f"Request was not successfull, check your `input configuation` and try again. Details: {details}",
            "index_error": f"Failed to access the Shopify store `{shop_name}`. Verify the entered Shopify store or API Key in `input configuration`.",
            "missing_token_error": "Authentication was unsuccessful. Please verify your authentication credentials or login is correct.",
            # add the other patterns and description, if needed...
        }
        return connection_check_errors_map.get(pattern)

    def test_connection(self) -> tuple[bool, str]:
        shop_name = self.config.get("shop")
        if not shop_name:
            return False, "The `Shopify Store` name is missing. Make sure it's entered and valid."

        try:
            response = list(self.test_stream.read_records(sync_mode=SyncMode.full_refresh))
            # check for the shop_id is present in the response
            shop_id = response[0].get("id")
            if shop_id is not None:
                return True, None
            else:
                return False, f"The `shop_id` is invalid: {shop_id}"
        except (SSLError, ConnectionError):
            return False, self.describe_error("connection_error", shop_name)
        except RequestException as req_error:
            return False, self.describe_error("request_exception", details=req_error)
        except IndexError:
            return False, self.describe_error("index_error", shop_name, response)
        except MissingAccessTokenError:
            return False, self.describe_error("missing_token_error")

    def get_shop_id(self) -> str:
        """
        We need to have the `shop_id` value available to have it passed elsewhere and fill-in the missing data.
        By the time this method is tiggered, we are sure we've passed the `Connection Checks` and have the `shop_id` value.
        """
        response = list(self.test_stream.read_records(sync_mode=SyncMode.full_refresh))
        if len(response) == 0:
            raise AirbyteTracedException(
                message=f"Could not find a Shopify shop with the name {self.config.get('shop', '')}. Make sure it's valid.",
                failure_type=FailureType.config_error,
            )
        shop_id = response[0].get("id")
        if shop_id:
            return shop_id
        else:
            raise Exception(f"Couldn't get `shop_id`. Actual `response`: {response}.")


class SourceShopify(AbstractSource):
    @property
    def continue_sync_on_stream_failure(self) -> bool:
        return True

    @property
    def raise_exception_on_missing_stream(self) -> bool:
        return False

    @staticmethod
    def get_shop_name(config) -> str:
        split_pattern = ".myshopify.com"
        shop_name = config.get("shop")
        return shop_name.split(split_pattern)[0] if split_pattern in shop_name else shop_name

    @staticmethod
    def format_stream_name(name) -> str:
        return "".join(x.capitalize() for x in name.split("_"))

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector.
        """
        config["shop"] = self.get_shop_name(config)
        config["authenticator"] = ShopifyAuthenticator(config)
        return ConnectionCheckTest(config).test_connection()

    def select_transactions_stream(self, config: Mapping[str, Any]) -> Stream:
        """
        Allow the Customer to decide which API type to use when it comes to the `Transactions` stream.
        """
        should_fetch_user_id = config.get("fetch_transactions_user_id")
        if should_fetch_user_id:
            return Transactions(config)
        else:
            return TransactionsGraphql(config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """
        config["shop"] = self.get_shop_name(config)
        config["authenticator"] = ShopifyAuthenticator(config)
        # add `shop_id` int value
        config["shop_id"] = ConnectionCheckTest(config).get_shop_id()
        # define scopes checker
        scopes_manager: ShopifyScopes = ShopifyScopes(config)
        # get the list of the permitted streams, based on the authenticated user scopes
        permitted_streams = scopes_manager.get_permitted_streams()
        stream_instances = [
            AbandonedCheckouts(config),
            Articles(config),
            BalanceTransactions(config),
            Blogs(config),
            Collections(config),
            Collects(config),
            CustomCollections(config),
            CustomerJourneySummary(config),
            Customers(config),
            DiscountCodes(config),
            Disputes(config),
            DraftOrders(config),
            FulfillmentOrders(config),
            Fulfillments(config),
            InventoryItems(config),
            InventoryLevels(config),
            Locations(config),
            MetafieldArticles(config),
            MetafieldBlogs(config),
            MetafieldCollections(config),
            MetafieldCustomers(config),
            MetafieldDraftOrders(config),
            MetafieldLocations(config),
            MetafieldOrders(config),
            MetafieldPages(config),
            MetafieldProductImages(config),
            MetafieldProducts(config),
            MetafieldProductVariants(config),
            MetafieldShops(config),
            MetafieldSmartCollections(config),
            OrderRefunds(config),
            OrderRisks(config),
            Orders(config),
            Pages(config),
            PriceRules(config),
            ProductImages(config),
            Products(config),
            ProductsGraphQl(config),
            ProductVariants(config),
            Shop(config),
            SmartCollections(config),
            TenderTransactions(config),
            self.select_transactions_stream(config),
            CustomerSavedSearch(config),
            CustomerAddress(config),
            Countries(config),
        ]

        return [
            stream_instance for stream_instance in stream_instances if self.format_stream_name(stream_instance.name) in permitted_streams
        ]
