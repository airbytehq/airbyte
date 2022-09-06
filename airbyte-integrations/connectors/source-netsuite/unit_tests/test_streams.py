#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pytest

from source_netsuite.streams import (
    Accounts,
    Classifications,
    Currencies,
    Customers,
    Departments,
    Employees,
    ExpenseCategories,
    ExpenseReports,
    Files,
    Folders,
    JournalEntries,
    Locations,
    Projects,
    Subsidiaries,
    TaxGroups,
    TaxItems,
    Terms,
    VendorBills,
    VendorPayments,
    Vendors,
)


@pytest.fixture(autouse=True)
def config_file():
    return {
      "realm": "1234567_SB1",
      "consumer_key": "0...",
      "consumer_secret": "8...",
      "token_id": "8...",
      "token_secret": "a..."
    }


@pytest.fixture(autouse=True)
def all_streams():
    return (
        Accounts,
        Classifications,
        Currencies,
        Customers,
        Departments,
        Employees,
        ExpenseCategories,
        ExpenseReports,
        Files,
        Folders,
        JournalEntries,
        Locations,
        Projects,
        Subsidiaries,
        TaxGroups,
        TaxItems,
        Terms,
        VendorBills,
        VendorPayments,
        Vendors,
    )

def test_init_streams(all_streams, config_file):

    #_nc = SourceNetsuiteSoap.get_netsuite_connector(config_file)
    for each_stream in all_streams:
        # _init_stream = each_stream(nc=_nc, config=config_file)
        # assert _init_stream != None
        assert each_stream.primary_key != None and each_stream.name != None
