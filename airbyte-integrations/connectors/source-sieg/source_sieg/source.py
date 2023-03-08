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
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from source_sieg.config import cnpj_map
from threading import Thread, Event
from threading import Lock
from source_sieg.thread_safe_list import ThreadSafeList


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
        self.threads_quantity = 64
        self.max_skip = 1000000

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

    def get_payload_skip(self, skip):
        payload = {
            "apikey": self.api_key,
            "email": self.email,
            "xmltype": self.xmltype,
            "take": self.take,
            "skip": skip,
            "dataInicio": self.start_date,
            "dataFim": self.end_date,
            "downloadevent": self.downloadevent
        }
        return payload

    def get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        return headers
    
    def get_url(self):
        return "https://api.sieg.com/aws/api-xml-search.ashx"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

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

        logger.info(f"Collected Invoice: {invoice_id}")

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

    def format_response(self, response):

        xml = response['xmls'][0]
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
        return invoice


    def chunker_list(self, list, size):
        return (list[i::size] for i in range(size))

    def make_request(self,url,payload,headers):
        response = requests.request("POST", url=url, data=payload, headers=headers)
        return response

    def read_invoice(self, item_list, skips_list):
        for skip in skips_list:
            logger.info(f'--- Running {self.class_identifier} --- Skip: {skip}')

            payload = json.dumps(self.get_payload_skip(skip))
            headers = self.get_headers()
            url = self.get_url()

            response = self.make_request(url=url,payload=payload,headers=headers)

            try:
                if response.json()['xmls']:
                    invoice = self.format_response(response.json())
                else:
                    logger.info('--- Breaking Thread')
                    break
                
                item_list.append(invoice)
            except:
                logger.info('--- Empity Response')
                self.read_invoice(item_list, skips_list)
                
    
    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):

        logger.info("Parsing Response")

        skips_list = [i for i in range(0,self.max_skip)]
        item_list = ThreadSafeList()
        threads_quantity = self.threads_quantity

        threads = []
        events = Event()
        for chunk in self.chunker_list(skips_list, threads_quantity):
            threads.append(Thread(target=self.read_invoice, args=(item_list, chunk)))

        # start threads
        for thread in threads:
            thread.start()
        
        # wait for all threads
        for thread in threads:
            thread.join()
        
        return item_list.get_list()


class Nfe(BaseClass):
    xmltype = "nfe"
    downloadevent = False
    class_identifier = "NFe"

    def get_created_at(self, xml_item):
        try:
            return xml_item["nfeProc"]["NFe"]["infNFe"]["ide"]["dhEmi"]
        except:
            logger.info(f"Didn't find the PROC field:\n {xml_item}")
            return xml_item["NFe"]["infNFe"]["ide"]["dhEmi"]
    
    def get_invoice_id(self, xml_item):
        try:
            return xml_item["nfeProc"]["NFe"]["infNFe"]["@Id"]
        except:
            logger.info(f"Didn't find the PROC field:\n {xml_item}")
            return xml_item["NFe"]["infNFe"]["@Id"]

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
    class_identifier = "CTe"

    def get_created_at(self, xml_item):
        try:
            return xml_item["cteProc"]["CTe"]["infCte"]["ide"]["dhEmi"]
        except:
            logger.info(f"Didn't find the PROC field:\n {xml_item}")
            return xml_item["CTe"]["infCte"]["ide"]["dhEmi"]
    
    def get_invoice_id(self, xml_item):
        try:
            return xml_item["cteProc"]["CTe"]["infCte"]["@Id"]
        except:
            logger.info(f"Didn't find the PROC field:\n {xml_item}")
            return xml_item["CTe"]["infCte"]["@Id"]

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
    class_identifier = "Evento_NFe"

    def get_invoice_type(self, xml_item):
        return "evento_nfe"

class CteEvents(Cte):
    xmltype = "cte"
    downloadevent = True
    class_identifier = "Evento_CTe"

    def get_invoice_type(self, xml_item):
        return "evento_cte"


class SourceSieg(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        payload = json.dumps({
            "apikey": config["api_key"],
            "email": config["email"],
            "xmltype": "nfe",
            "take": 1,
            "skip": 0,
            "dataInicio": config["start_date"],
            "dataFim": config["end_date"],
            "downloadevent": False
        })
        headers = {
            "Content-Type": "application/json"
        }
        url = "https://api.sieg.com/aws/api-xml-search.ashx"

        response = requests.request("POST", url=url, data=payload, headers=headers)

        if response.json()['xmls']:
            return True, None
        else:
            return None

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
