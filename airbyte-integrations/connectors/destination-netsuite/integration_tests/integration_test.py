import pytest

from destination_netsuite.netsuite.service import JournalEntry
from json import loads

def _payload(json_path: str):
    with open(json_path) as f:
        json = loads(f.read())
    return json

async def _journal_entry_post(payload_path: str, journal_entry: JournalEntry):
    resp = await journal_entry.add(_payload(payload_path))
    print(resp)

async def _journal_entry_get(request_path: str, journal_entry: JournalEntry):
    resp = await journal_entry.get(request_path,)
    print(resp)    

@pytest.mark.asyncio
async def test_post_payment(journal_entry):  
    resp = await _journal_entry_post('integration_tests/payment_req.json', journal_entry)
    print(resp)

@pytest.mark.asyncio
async def test_get_payment(journal_entry):  
    resp = await _journal_entry_get('/5/line/3', journal_entry)
    print(resp)

@pytest.mark.asyncio
async def test_post_revenue(journal_entry):
    resp = await _journal_entry_post('integration_tests/revenue_req.json', journal_entry)
    print(resp)

@pytest.mark.asyncio
async def test_post_client_refund(journal_entry):
    resp = await _journal_entry_post('integration_tests/client_refund_req.json', journal_entry)
    print(resp)

@pytest.mark.asyncio
async def test_post_merchant_settlement(journal_entry):
    resp = await _journal_entry_post('integration_tests/merchant_settlement_req.json', journal_entry)
    print(resp)