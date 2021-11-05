#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple
import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_vtex.streams.orders import Orders
from source_vtex.streams.order_details import OrderDetails
from source_vtex.streams.products_id_and_sku import ProductsIdAndSku
from source_vtex.streams.products import Products
from source_vtex.streams.products_detailed import ProductsDetailed


class VtexAuthenticator(requests.auth.AuthBase):
    def __init__(self, client_name, app_key, app_token):
        self.app_key = app_key
        self.app_token = app_token
        self.client_name = client_name

    def __call__(self, r):
        r.headers["x-vtex-api-appkey"] = self.app_key
        r.headers["x-vtex-api-apptoken"] = self.app_token

        return r


class SourceVtex(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided
            config can be used to connect to VTEX API

        :param config:  the user-input config object conforming to the
            connector's spec.json

        :param logger:  logger object

        :return Tuple[bool, any]: (True, None) if the input config can be used
            to connect to the API successfully, (False, error) otherwise.
        """
        app_key = config["app_key"]
        app_token = config["app_token"]
        client_name = config["client_name"]
        start_date = config["start_date"]

        authenticator = VtexAuthenticator(client_name, app_key, app_token)

        stream = Orders(authenticator=authenticator, start_date=start_date)

        return stream.check_connection()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in
            the connector spec.
        """
        app_key = config["app_key"]
        app_token = config["app_token"]
        client_name = config["client_name"]
        start_date = config["start_date"]

        authenticator = VtexAuthenticator(client_name, app_key, app_token)
        orders_stream = Orders(
            authenticator=authenticator, start_date=start_date
        )

        order_details_stream = OrderDetails(
            authenticator=authenticator,
            start_date=start_date,
            parent=orders_stream,
        )

        products_id_sku_stream = ProductsIdAndSku(
            authenticator=authenticator, start_date=start_date
        )

        products_stream = Products(
            authenticator=authenticator,
            start_date=start_date,
            parent=products_id_sku_stream,
        )

        product_details_stream = ProductsDetailed(
            authenticator=authenticator,
            start_date=start_date,
            parent=products_id_sku_stream,
        )

        return [
            orders_stream,
            order_details_stream,
            products_id_sku_stream,
            products_stream,
            product_details_stream,
        ]
