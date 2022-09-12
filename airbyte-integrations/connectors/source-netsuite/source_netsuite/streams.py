#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping, Optional, Union

import zeep
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class NetsuiteStream(HttpStream):

    def __init__(self, config: dict):
        self.netsuite_con = config["netsuite_con"]

    primary_key = "internalId"
    
    @property
    def url_base(self) -> str:
        return "/"
    
    @property
    def data_structure(self) -> str:
        return "list"

    def path(self, **kwargs) -> str:
        return self.name
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}
    
    @staticmethod
    def as_serialized(record) -> Iterable[Mapping[str, Any]]:
        return [zeep.helpers.serialize_object(_) for _ in record]
    
    def get_stream(self, stream_name: str) -> Union[object, None]:
        try:
            # get stream object reference from NetsuiteConnection
            return getattr(self.netsuite_con, stream_name)
        except AttributeError:
            self.logger.info(f"Stream `{stream_name}` is not available for NetsuiteConnection. Skipping...")
            return None
    
    def fetch_records(self) -> Union[Iterable[Mapping[str, Any]], None]:
        stream = self.get_stream(self.name)
        if stream:
            # prepare build-in generator for data fetch
            records_producer = stream.get_all_generator()
            # some streams return data as OrderedDict
            if self.data_structure == "dict":
                yield records_producer
            else:
                yield from records_producer
        return None

    def read_records(self, sync_mode: SyncMode, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in self.fetch_records():
            yield from self.as_serialized(record)


class Accounts(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3739999.html"""
    

class BillingAccounts(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4779334000.html"""
    

class Classifications(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3741163.html"""


class Departments(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3742370.html"""


class Currencies(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3741577.html"""
    
    data_structure = "dict"
    

class Locations(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3747661.html"""


class VendorBills(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3694535.html"""
    
    data_structure = "dict"
    

class Vendors(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3767893.html"""


class VendorPayments(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3695867.html"""
    
    data_structure = "dict"
    

class Subsidiaries(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3754626.html"""


class JournalEntries(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3683608.html"""
    
    data_structure = "dict"
    

class Employees(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/preface_3714104131.html"""


class ExpenseCategories(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N913978.html"""


class ExpenseReports(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N908140.html"""
    
    data_structure = "dict"
    

class Folders(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3784601.html"""


class Files(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3784054.html"""


class Customers(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3639940.html"""


class Projects(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/preface_3714107248.html"""


class Terms(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3767518.html"""


class TaxItems(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3755370.html"""


class TaxGroups(NetsuiteStream):
    """https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3755021.html"""

