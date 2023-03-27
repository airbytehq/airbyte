#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import io
import os
import time
import json
import zipfile
import requests
import xmltodict
import xml.etree.ElementTree as ET
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple


class MeliInvoices(HttpStream):

    url_base = "http://api.mercadolibre.com/"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.refresh_token = config["refresh_token"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.year_month = config["year_month"]
        self.access_token = self.get_access_token()
    
    def get_access_token(self):
        url = "https://api.mercadolibre.com/oauth/token"

        payload = json.dumps({
            "grant_type":"refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        access_token = response.json()["access_token"] 
        refresh_token = response.json()["refresh_token"]
        logger.info(f"Access Token: {access_token}")
        logger.info(f"Access Token: {refresh_token}")
        return access_token

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        # return f"users/{self.client_id}/invoices/sites/MLB/batch_request/period/stream?start={self.start_date}&end={self.end_date}"
        return f"users/{self.client_id}/invoices/sites/MLB/batch_request/period/{self.year_month}"
    
    def request_headers(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Mapping[str, Any]:
        """
        Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {'Authorization': f'Bearer {self.access_token}'}
    
    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):

        logger.info("Parsing Response")

        logger.info("Saving XML files locally")
        zfile = zipfile.ZipFile(io.BytesIO(response.content))
        zfile.extractall()
        time.sleep(10)

        path_meli = './emitidas_mercado_livre/xml'
        path_outro_erp = './emitidas_outro_erp/xml'
        paths = [path_meli, path_outro_erp]

        logger.info("Iterating through the xml folders to unify all xmls in just one object")
        items = []
        for path in paths:
            for filename in os.listdir(path):
                if not filename.endswith('.xml'): continue
                fullname = os.path.join(path, filename)
                tree = ET.parse(fullname)
            
                # Trasforming XML in string
                root = tree.getroot()
                xml = ET.tostring(root)

                # Transforming XML in json
                xml = xmltodict.parse(xml)
                items.append(xml)

        # with open('./invoices.json', 'w+') as f:
        #     json.dump(items, f)
        #     f.truncate()
        # ns0:nfeProc
        # ns0:procEventoNFe

        return items


class SourceMeliFull(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()

        return [
            MeliInvoices(authenticator=auth, config=config)
        ]
