#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import base64
import logging
import requests
import xmltodict
from lxml import etree
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from source_sieg.config import cnpj_map


class BaseClass(HttpStream):

    url_base = "https://api.sieg.com/"
    http_method = "POST"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.email = config["email"]
        self.start_date = config["start_date"]
        self.end_date = config["end_date"]
        self.take = 1
        self.skip = 0
        self.downloadevent = False

    @abstractmethod
    def xmltype(self) -> str:
        """
        :return: XML Type. It can be nfe or cte.
        """
    
    @abstractmethod
    def downloadevent(self) -> str:
        """
        :return: Boolean value that defines whether the events will be downloaded or not.
        """
    
    def get_merchant_uid(self, cnpjs):
        for cnpj in cnpjs:
            merchant_uid = cnpj_map.get(cnpj)
            if merchant_uid:
                return merchant_uid
        return None

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:

        payload = {
            "apikey": self.api_key,
            "email": self.email,
            "xmltype": self.xmltype,
            "take": self.take,
            "skip": self.skip,
            "dataInicio": self.start_date,
            "dataFim": self.end_date,
            "downloadevent": self.downloadevent
        }

        return payload

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if not response.json()['xmls']:
            print(f'Finished processing {self.xmltype}')
            return None
        else:
            self.skip += 1
            print(f'Processing {self.xmltype} ---- skip - {self.skip}')
            return True

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "aws/api-xml-search.ashx"
    

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:

        created_at = self.get_created_at(xml_item)
        invoice_id = self.get_invoice_id(xml_item)
        invoice_type = self.get_invoice_type(xml_item)
        cnpjs = self.get_cnpjs(xml_item)

        merchant = self.get_merchant_uid(cnpjs)

        invoice = {
            "data": xml_item,
            "merchant": merchant,
            "source": "BR_SIEG",
            "type": f"{merchant}_invoice",
            "id": invoice_id,
            "timeline": "historic",
            "invoice_id": invoice_id,
            "created_at": created_at,
            "updated_at": created_at,
            "cnpjs": cnpjs,
            "invoice_type": invoice_type,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }

        return invoice
    
    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        response = response.json()
        items = []

        try:
            for xml in response['xmls']:

                xml = base64.b64decode(xml)

                try:
                    xml_to_dict = xmltodict.parse(xml)
                except:
                    parser = etree.XMLParser(recover=True)
                    root = etree.fromstring(xml, parser)
                    xml = etree.tostring(root)
                    xml_to_dict = xmltodict.parse(xml)

                xml = xml_to_dict

                invoice = self.format_xml(xml)
                items.append(invoice)
        except:
            print("Empity XMLNS")
            print(f"--- Response: {response.text}")
            pass
        
        return items


class Nfe(BaseClass):
    xmltype = "nfe"
    downloadevent = False

    def get_created_at(self, xml_item):
        return xml_item["nfeProc"]["NFe"]["infNFe"]["ide"]["dhEmi"]
    
    def get_invoice_id(self, xml_item):
        return xml_item["nfeProc"]["NFe"]["infNFe"]["@Id"]

    def get_invoice_type(self, xml_item):
        tpnf = xml_item["nfeProc"]["NFe"]["infNFe"]["ide"]["tpNF"]
        if tpnf == "0":
            return "inbound"
        elif tpnf == "1":
            return "outbound"
        else:
            return "unknown"
    
    def get_cnpjs(self, xml_item):
        cnpjs = []

        try:
            cnpj_emit = xml_item["nfeProc"]["NFe"]["infNFe"]["emit"]["CNPJ"]
        except:
            cnpj_emit = None
        try:
            cnpj_dest = xml_item["nfeProc"]["NFe"]["infNFe"]["dest"]["CNPJ"]
        except:
            cnpj_dest = None
        try:
            cnpj_inf = xml_item["nfeProc"]["NFe"]["infNFe"]["infRespTec"]["CNPJ"]
        except:
            cnpj_inf = None
        
        cnpjs.append(cnpj_emit)
        cnpjs.append(cnpj_dest)
        cnpjs.append(cnpj_inf)
        
        return cnpjs


class Cte(BaseClass):
    xmltype = "cte"
    downloadevent = False

    def get_created_at(self, xml_item):
        return xml_item["cteProc"]["CTe"]["infCte"]["ide"]["dhEmi"]
    
    def get_invoice_id(self, xml_item):
        return xml_item["cteProc"]["CTe"]["infCte"]["@Id"]

    def get_invoice_type(self, xml_item):
        return "cte"
    
    def get_cnpjs(self, xml_item):
        cnpjs = []

        try:
            cnpj_emit = xml_item["cteProc"]["CTe"]["infCte"]["emit"]["CNPJ"]
        except:
            cnpj_emit = None
        try:
            cnpj_dest = xml_item["cteProc"]["CTe"]["infCte"]["dest"]["CNPJ"]
        except:
            cnpj_dest = None
        try:
            cnpj_inf = xml_item["cteProc"]["CTe"]["infCte"]["infRespTec"]["CNPJ"]
        except:
            cnpj_inf = None
        
        cnpjs.append(cnpj_emit)
        cnpjs.append(cnpj_dest)
        cnpjs.append(cnpj_inf)
        
        return cnpjs

class NfeEvents(Nfe):
    xmltype = "nfe"
    downloadevent = True

    def get_invoice_type(self, xml_item):
        return "evento_nfe"

class CteEvents(Cte):
    xmltype = "cte"
    downloadevent = True

    def get_invoice_type(self, xml_item):
        return "evento_cte"


class SourceSieg(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()

        return [
            Nfe(authenticator=auth, config=config),
            Cte(authenticator=auth, config=config),
            NfeEvents(authenticator=auth, config=config),
            CteEvents(authenticator=auth, config=config)
        ]
