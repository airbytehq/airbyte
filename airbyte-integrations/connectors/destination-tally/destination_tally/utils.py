#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, Mapping

import requests
from airbyte_cdk import AirbyteLogger


def clear_post_data(config: Mapping[str, Any], template_key: str, logger: AirbyteLogger):
    url = "https://api.excel2tally.in/api/User/ApproveDownload"
    headers = {
        "X-Auth-Key": config["auth_key"],
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Template-Key": template_key,
        "IsFileReceived": "true",
        "CompanyName": config["company_name"],
    }

    response = requests.request(method="POST", url=url, headers=headers)
    if response.status_code == 200:
        logger.info("previous post data for ledger cleared")
    else:
        logger.info("couldn't clear the post data")


def prepare_headers(config: Mapping[str, Any], template_key: str):
    headers = {
        "X-Auth-Key": config["auth_key"],
        "Template-Key": template_key,
        "CompanyName": config["company_name"],
        "version": config["version"],
        "Content-Type": "application/json",
    }
    return headers


# 1. Ledger Master Template - (Date format : mm-dd-yyyy)
def prepare_ledger_master_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    Args : data to insert into tally
    Returns : ledger payload
    """
    required_fields = ["Ledger Name", "Group Name"]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    ledger_fields = [
        "Ledger Name",
        "Alias1",
        "Alias2",
        "Alias3",
        "Alias4",
        "Group Name",
        "Credit Period",
        "Address Line 1",
        "Address Line 2",
        "Address Line 3",
        "Address Line 4",
        "Country",
        "State",
        "Pincode",
        "Contact Person",
        "Phone No",
        "Mobile No",
        "Fax No",
        "Email",
        "Email CC",
        "Website",
        "PAN No",
        "GSTIN",
        "GST Reg Type",
        "Service Tax No",
        "VAT Tin No",
        "CST No",
        "VAT Reg Type",
        "Opening Balance",
        "Dr / Cr",
        "Bill Name",
        "Bill Date",
    ]

    ledger_master_payload = {}
    for key, value in data.items():
        if key in ledger_fields:
            ledger_master_payload[key] = value

    return json.dumps({"body": [ledger_master_payload]})


def insert_ledger_master_to_tally(config: Mapping[str, Any], data: Dict[str, Any], ledger_master_template_url: str, logger: AirbyteLogger):
    """
    Prepares headers and payload for ledger and makes a post request to insert ledger into tally
    """
    ledger_master_template_key = "16"

    ledger_master_headers = prepare_headers(config=config, template_key=ledger_master_template_key)
    ledger_master_headers["AddAutoMaster"] = "0"
    ledger_master_headers["Automasterids"] = "0"

    ledger_master_payload = prepare_ledger_master_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST", url=ledger_master_template_url, data=ledger_master_payload, headers=ledger_master_headers
        )
    except Exception as e:
        logger.error(f'request for ledger : {data["Ledger Name"]} not successful , {e}')
        return

    if response.status_code == 200:
        logger.info(f'ledger : {data["Ledger Name"]} successfully inserted into Tally')
    else:
        logger.info(f'ledger : {data["Ledger Name"]} cannot be inserted into Tally')


# 2. Journal Voucher Template - Date format problem
def prepare_journal_voucher_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Ledger Name
    2. Cost Center
    3. Stock Item
    4. Unit [UOM]
    5. Voucher Type
    """
    required_fields = ["Date", "Voucher Number", "Voucher Type", "Ledger Name", "Debit / Credit", "Amount"]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    journal_voucher_fields = [
        "Date",
        "Voucher Number",
        "Voucher Type",
        "Ledger Name",
        "Debit / Credit",
        "Amount",
        "Voucher Ref Date",
        "Bill Ref No",
        "Cost Center",
        "Stock Item",
        "Godown",
        "Batch No",
        "QTY",
        "Rate",
        "UOM",
        "Item Amount",
        "Narration",
    ]

    credit_payload = {"Debit / Credit": "Cr"}
    for key, value in data:
        if key in journal_voucher_fields:
            if key == "Debit / Credit" and (value == "Dr" or value == "Cr"):
                continue
            else:
                credit_payload[key] = value

    debit_payload = {"Debit / Credit": "Dr"}
    for key, value in data:
        if key in journal_voucher_fields:
            if key == "Debit / Credit" and (value == "Dr" or value == "Cr"):
                continue
            else:
                debit_payload[key] = value

    return json.dumps({"body": [credit_payload, debit_payload]})


def insert_journal_voucher_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], journal_voucher_template_url: str, logger: AirbyteLogger
):
    journal_voucher_template_key = "18"
    journal_voucher_headers = prepare_headers(config=config, template_key=journal_voucher_template_key)
    journal_voucher_payload = prepare_journal_voucher_payload(data=data, logger=logger)

    logger.info(f"headers : {journal_voucher_headers}")
    logger.info(f"payload : {journal_voucher_payload}")

    try:
        response = requests.request(
            method="POST", url=journal_voucher_template_url, data=journal_voucher_payload, headers=journal_voucher_headers
        )
    except Exception as e:
        logger.error(f"request for inserting journal was not successful , {e}")
        return

    if response.status_code == 200:
        logger.info("journal entry successfully inserted into Tally")
    else:
        logger.info("journal entry cannot be inserted into Tally")

    logger.info(f"result : {response.content}")


# 3. Item Master Template : (Date format : mm-dd-yyyy)
def prepare_item_master_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    Args: Stock item data to insert into tally
    Returns : item payload

    Already Required entries in tally :
    1. Stock Group ["Group Name"]
    2. Stock Category ["Category Name"]
    3. unit ["UOM]
    """
    required_fields = ["Item Name", "UOM"]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    item_master_fields = [
        "Item Name",
        "UOM",
        "Item Code / Alias 1",
        "Item Code / Alias 2",
        "Item Code / Alias 3",
        "Item Code / Alias 4",
        "Item Code / Alias 5",
        "Item Code / Alias 6",
        "Part No",
        "Item Description",
        "Standard Cost",
        "Standard Selling Price",
        "Applicable From (SC / SP)",
        "MRP",
        "MRP Applicable From",
        "HSN Code",
        "HSN Description",
        "Taxability",
        "GST Rate",
        "Applicable From",
        "Group Name",
        "Category Name",
        "Godown",
        "Batch",
        "Opening QTY",
        "Rate",
        "Amount",
    ]

    item_master_payload = {}
    for key, value in data.items():
        if key in item_master_fields:
            item_master_payload[key] = value

    return json.dumps({"body": [item_master_payload]})


def insert_item_master_to_tally(config: Mapping[str, Any], data: Dict[str, Any], item_master_template_url: str, logger: AirbyteLogger):
    """
    Prepares headers and payload for stock item to make a post request to insert stock item into tally
    """
    item_master_template_key = "15"
    item_master_headers = prepare_headers(config=config, template_key=item_master_template_key)
    item_master_payload = prepare_item_master_payload(data=data, logger=logger)

    try:
        response = requests.request(method="POST", url=item_master_template_url, data=item_master_payload, headers=item_master_headers)
    except Exception as e:
        logger.error(f'request for item : {data["Item Name"]} not successful, {e}')
        return

    if response.status_code == 200:
        logger.info(f'item : {data["Item Name"]} successfully inserted into Tally')
    else:
        logger.info(f'item : {data["Item Name"]} cannot be inserted into Tally')


# 4. Sales order Template - Date format problem
def prepare_sales_order_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Unit [UOM]
    2. Sales Ledger
    3. Other Charges_1 Ledger
    4. Other Charges_2 Ledger
    5. SGST Ledger
    6. CGST Ledger
    7. IGST Ledger
    8. Cost Center
    """
    required_fields = [
        "Date",
        "Voucher Number",
        "Voucher Type",
        "Customer Name",
        "Order No",
        "Due On",
        "Item Name",
        "Tax Rate",
        "QTY",
        "UOM",
        "Rate",
        "Amount",
    ]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    sales_order_fields = [
        "Date",
        "Voucher Number",
        "Voucher Type",
        "Customer Name",
        "Address 1",
        "Address 2",
        "Address 3",
        "State",
        "Tin No",
        "CST No",
        "GSTIN",
        "Term of Payment",
        "Other Reference",
        "Terms of Delivery",
        "Dispatch Through",
        "Destination",
        "Order No",
        "Due On",
        "Item Name",
        "Item Description",
        "Tax Rate",
        "Batch No",
        "Mfg Date",
        "Exp Date",
        "QTY",
        "UOM",
        "Rate",
        "Discount %",
        "Amount",
        "Sales Ledger",
        "Other Charges_1 Amount",
        "Other Charges_1 Ledger",
        "Other Charges_2 Amount",
        "Other Charges_2 Ledger",
        "SGST Amount",
        "SGST Ledger",
        "CGST Amount",
        "CGST Ledger",
        "IGST Amount",
        "IGST Ledger",
        "Cost Center",
        "Godown",
        "Narration",
    ]

    sales_order_payload = {}
    for key, value in data.items():
        if key in sales_order_fields:
            sales_order_payload[key] = value

    return json.dumps({"body": [sales_order_payload]})


def insert_sales_order_to_tally(config: Mapping[str, Any], data: Dict[str, Any], sales_order_template_url: str, logger: AirbyteLogger):
    sales_order_template_key = "3"
    sales_order_headers = prepare_headers(config=config, template_key=sales_order_template_key)
    sales_order_payload = prepare_sales_order_payload(data=data, logger=logger)

    try:
        response = requests.request(method="POST", url=sales_order_template_url, data=sales_order_payload, headers=sales_order_headers)
    except Exception as e:
        logger.error(f"request for sales order not successful, {e}")
        return

    if response.status_code == 200:
        logger.info("sales order successfully inserted into Tally")
    else:
        logger.info("sales order cannot be inserted into Tally")


# 5. Payment Voucher Template - *** Working *** (Bill Date format : dd-mm-yyyy)
def prepare_payment_voucher_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    Args : Payment voucher data
    Returns : Payment voucher payload

    Already required entries in tally :
    1. Debit Ledgers [Ledger]
    2. Cash/Bank Ledger [Ledger]
    3. Cost Centre
    """
    required_fields = ["Voucher Date", "Voucher Number", "Voucher Type", "Cash/Bank Ledger", "Debit Ledgers", "Amount", "Instrument Type"]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    payment_voucher_fields = [
        "Voucher Date",
        "Reco Date",
        "Voucher Number",
        "Voucher Type",
        "Cash/Bank Ledger",
        "Debit Ledgers",
        "Bill Name",
        "Amount",
        "Instrument Type",
        "Instrument Number",
        "Instrument Date",
        "Cost Center",
        "Narration",
    ]

    payment_voucher_payload = {}
    for key, value in data.items():
        if key in payment_voucher_fields:
            payment_voucher_payload[key] = value

    return json.dumps({"body": [payment_voucher_payload]})


def insert_payment_voucher_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], payment_voucher_template_url: str, logger: AirbyteLogger
):
    """
    Prepares headers and payload to make post request to insert payment voucher into tally
    """
    payment_voucher_template_key = "13"
    payment_voucher_headers = prepare_headers(config=config, template_key=payment_voucher_template_key)
    payment_voucher_payload = prepare_payment_voucher_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST", url=payment_voucher_template_url, data=payment_voucher_payload, headers=payment_voucher_headers
        )
    except Exception as e:
        logger.error(f"request for payment voucher not successful : {e}")
        return

    if response.status_code == 200:
        logger.info(f'payment voucher with voucher number : {payment_voucher_payload["Voucher Number"]} successfully inserted into Tally')
    else:
        logger.info(f'payment voucher with voucher number : {payment_voucher_payload["Voucher Number"]} cannot be inserted into Tally')


# 6. Receipt Voucher Template - Date format problem
def prepare_receipt_voucher_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Credit Ledgers [Ledger]
    2. Cash / Bank Ledger [Ledger]
    3. Ledger / Item
    4. Cost Center
    5. Voucher Type
    """
    required_fields = ["Voucher Date", "Voucher Number", "Voucher Type", "Credit Ledgers", "Cash / Bank Ledger", "Amount"]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    receipt_voucher_fields = [
        "Voucher Date",
        "Voucher Number",
        "Voucher Type",
        "Bank Reco Date",
        "Is Advance Receipt",
        "Credit Ledgers",
        "Party Name",
        "Add 1",
        "Add 2",
        "Add 3",
        "State",
        "Place of Supply",
        "Registration Type",
        "GSTIN",
        "Cash / Bank Ledger",
        "Bill Name",
        "Amount",
        "Ledger / Item",
        "Taxable Value",
        "CGST Rate",
        "CGST Amount",
        "SGST Rate",
        "SGST Amount",
        "IGST Rate",
        "IGST Amount",
        "Instrument Type",
        "Instrument Number",
        "Instrument Date",
        "Issued Bank",
        "Branch",
        "Cost Center",
        "Narration",
    ]

    receipt_voucher_payload = {}
    for key, value in data.items():
        if key in receipt_voucher_fields:
            receipt_voucher_payload[key] = value

    return json.dumps({"body": [receipt_voucher_payload]})


def insert_receipt_voucher_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], receipt_voucher_template_url: str, logger: AirbyteLogger
):
    receipt_voucher_template_key = "12"
    receipt_voucher_headers = prepare_headers(config=config, template_key=receipt_voucher_template_key)
    receipt_voucher_payload = prepare_receipt_voucher_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST", url=receipt_voucher_template_url, data=receipt_voucher_payload, headers=receipt_voucher_headers
        )
    except Exception as e:
        logger.error(f"request for receipt voucher not successful, {e}")
        return

    if response.status_code == 200:
        logger.info("receipt voucher successfully inserted into Tally")
    else:
        logger.info("receipt voucher cannot be inserted into Tally")

    logger.info(f"result : {response.content}")


# 7. Debit note without inventory Template - Date format problem
def prepare_debitnote_without_inventory_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Debit / Party Ledger
    2. Credit Ledger 1 , 2 , and so on
    3. Cost Center
    """
    required_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "Reason Code",
        "Debit / Party Ledger",
        "Credit Ledger 1",
        "Credit Ledger 1 Amount",
    ]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    debitnote_without_inventory_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "Original Invoice No",
        "Original Invoice Date",
        "Reason Description",
        "Reason Code",
        "Supplier DN No",
        "Supplier DN Date",
        "Credit Period",
        "Debit / Party Ledger",
        "Address 1",
        "Address 2",
        "Address 3",
        "Address 4",
        "State",
        "Place of Supply",
        "Country",
        "GSTIN",
        "GST Registration Type",
        "Credit Ledger 1",
        "Credit Ledger 1 Amount",
        "Credit Ledger 2",
        "Credit Ledger 2 Amount",
        "Credit Ledger 3",
        "Credit Ledger 3 Amount",
        "Credit Ledger 4",
        "Credit Ledger 4 Amount",
        "Credit Ledger 5",
        "Credit Ledger 5 Amount",
        "Credit Ledger 6",
        "Credit Ledger 6 Amount",
        "Credit Ledger 7",
        "Credit Ledger 7 Amount",
        "Credit Ledger 8",
        "Credit Ledger 8 Amount",
        "Credit Ledger 9",
        "Credit Ledger 9 Amount",
        "Credit Ledger 10",
        "Credit Ledger 10 Amount",
        "Credit Ledger 11",
        "Credit Ledger 11 Amount",
        "Credit Ledger 12",
        "Credit Ledger 12 Amount",
        "Credit Ledger 13",
        "Credit Ledger 13 Amount",
        "Credit Ledger 14",
        "Credit Ledger 14 Amount",
        "Credit Ledger 15",
        "Credit Ledger 15 Amount",
        "Credit Ledger 16",
        "Credit Ledger 16 Amount",
        "Credit Ledger 17",
        "Credit Ledger 17 Amount",
        "Credit Ledger 18",
        "Credit Ledger 18 Amount",
        "Credit Ledger 19",
        "Credit Ledger 19 Amount",
        "Credit Ledger 20",
        "Credit Ledger 20 Amount",
        "Credit Ledger 21",
        "Credit Ledger 21 Amount",
        "Credit Ledger 22",
        "Credit Ledger 22 Amount",
        "Credit Ledger 23",
        "Credit Ledger 23 Amount",
        "Credit Ledger 24",
        "Credit Ledger 24 Amount",
        "Credit Ledger 25",
        "Credit Ledger 25 Amount",
        "Credit Ledger 26",
        "Credit Ledger 26 Amount",
        "Credit Ledger 27",
        "Credit Ledger 27 Amount",
        "Credit Ledger 28",
        "Credit Ledger 28 Amount",
        "Credit Ledger 29",
        "Credit Ledger 29 Amount",
        "Credit Ledger 30",
        "Credit Ledger 30 Amount",
        "Cost Center",
        "Narration",
    ]

    debitnote_without_inventory_payload = {}
    for key, value in data.items():
        if key in debitnote_without_inventory_fields:
            debitnote_without_inventory_payload[key] = value

    return json.dumps({"body": [debitnote_without_inventory_payload]})


def insert_debitnote_without_inventory_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], debitnote_without_inventory_template_url: str, logger: AirbyteLogger
):
    debitnote_without_inventory_template_key = "11"
    debitnote_without_inventory_headers = prepare_headers(config=config, template_key=debitnote_without_inventory_template_key)
    debitnote_without_inventory_payload = prepare_debitnote_without_inventory_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST",
            url=debitnote_without_inventory_template_url,
            data=debitnote_without_inventory_payload,
            headers=debitnote_without_inventory_headers,
        )
    except Exception as e:
        logger.error(f"request for debit note not successful, {e}")
        return

    if response.status_code == 200:
        logger.info("debit note successfully inserted into Tally")
    else:
        logger.info("debit note cannot be inserted into Tally")


# 8. Purchase without inventory Template - Date format problem
def prepare_purchase_without_inventory_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Credit / Party Ledger
    2. Debit Ledger 1 , 2 , and so on
    3. Cost Center
    """
    required_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "Credit / Party Ledger",
        "Debit Ledger 1",
        "Debit Ledger 1 Amount",
    ]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    purchase_without_inventory_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "IS Invoice",
        "Supplier Inv No",
        "Supplier Inv Date",
        "Credit / Party Ledger",
        "Address 1",
        "Address 2",
        "Address 3",
        "Address 4",
        "State",
        "Place of Supply",
        "VAT Tin No",
        "CST No",
        "Service Tax No",
        "GSTIN",
        "GST Registration Type",
        "Debit Ledger 1",
        "Debit Ledger 1 Amount",
        "Ledger 1 Description",
        "Debit Ledger 2",
        "Debit Ledger 2 Amount",
        "Ledger 2 Description",
        "Debit Ledger 3",
        "Debit Ledger 3 Amount",
        "Ledger 3 Description",
        "Debit Ledger 4",
        "Debit Ledger 4 Amount",
        "Ledger 4 Description",
        "Debit Ledger 5",
        "Debit Ledger 5 Amount",
        "Ledger 5 Description",
        "Debit Ledger 6",
        "Debit Ledger 6 Amount",
        "Ledger 6 Description",
        "Debit Ledger 7",
        "Debit Ledger 7 Amount",
        "Ledger 7 Description",
        "Debit Ledger 8",
        "Debit Ledger 8 Amount",
        "Ledger 8 Description",
        "Debit Ledger 9",
        "Debit Ledger 9 Amount",
        "Ledger 9 Description",
        "Debit Ledger 10",
        "Debit Ledger 10 Amount",
        "Ledger 10 Description",
        "Debit Ledger 11",
        "Debit Ledger 11 Amount",
        "Ledger 11 Description",
        "Debit Ledger 12",
        "Debit Ledger 12 Amount",
        "Ledger 12 Description",
        "Debit Ledger 13",
        "Debit Ledger 13 Amount",
        "Ledger 13 Description",
        "Debit Ledger 14",
        "Debit Ledger 14 Amount",
        "Ledger 14 Description",
        "Debit Ledger 15",
        "Debit Ledger 15 Amount",
        "Ledger 15 Description",
        "Debit Ledger 16",
        "Debit Ledger 16 Amount",
        "Ledger 16 Description",
        "Debit Ledger 17",
        "Debit Ledger 17 Amount",
        "Ledger 17 Description",
        "Debit Ledger 18",
        "Debit Ledger 18 Amount",
        "Ledger 18 Description",
        "Debit Ledger 19",
        "Debit Ledger 19 Amount",
        "Ledger 19 Description",
        "Debit Ledger 20",
        "Debit Ledger 20 Amount",
        "Ledger 20 Description",
        "Debit Ledger 21",
        "Debit Ledger 21 Amount",
        "Ledger 21 Description",
        "Debit Ledger 22",
        "Debit Ledger 22 Amount",
        "Ledger 22 Description",
        "Debit Ledger 23",
        "Debit Ledger 23 Amount",
        "Ledger 23 Description",
        "Debit Ledger 24",
        "Debit Ledger 24 Amount",
        "Ledger 24 Description",
        "Debit Ledger 25",
        "Debit Ledger 25 Amount",
        "Ledger 25 Description",
        "Debit Ledger 26",
        "Debit Ledger 26 Amount",
        "Ledger 26 Description",
        "Debit Ledger 27",
        "Debit Ledger 27 Amount",
        "Ledger 27 Description",
        "Debit Ledger 28",
        "Debit Ledger 28 Amount",
        "Ledger 28 Description",
        "Debit Ledger 29",
        "Debit Ledger 29 Amount",
        "Ledger 29 Description",
        "Debit Ledger 30",
        "Debit Ledger 30 Amount",
        "Ledger 30 Description",
        "Debit Period",
        "Cost Center",
        "Narration",
    ]

    purchase_without_inventory_payload = {}
    for key, value in data.items():
        if key in purchase_without_inventory_fields:
            purchase_without_inventory_payload[key] = value

    return json.dumps({"body": [purchase_without_inventory_payload]})


def insert_purchase_without_inventory_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], purchase_without_inventory_template_url: str, logger: AirbyteLogger
):
    purchase_without_inventory_template_key = "8"
    purchase_without_inventory_headers = prepare_headers(config=config, template_key=purchase_without_inventory_template_key)
    purchase_without_inventory_payload = prepare_purchase_without_inventory_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST",
            url=purchase_without_inventory_template_url,
            data=purchase_without_inventory_payload,
            headers=purchase_without_inventory_headers,
        )
    except Exception as e:
        logger.error(f"request for purchase without inventory not successful, {e}")
        return

    if response.status_code == 200:
        logger.info("purchase without inventory successfully inserted into Tally")
    else:
        logger.info("purchase without inventory cannot be inserted into Tally")


# 9. Credit Note without inventory Template - Date format problem
def prepare_creditnote_without_inventory_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Credit / Party Ledger
    2. Debit Ledger 1 , 2 , and so on
    3. Cost Center
    """
    required_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "Reason Code" "Credit / Party Ledger",
        "Debit Ledger 1",
        "Debit Ledger 1 Amount",
    ]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    debitnote_without_inventory_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "Original Invoice No",
        "Original Invoice Date",
        "Ref No / Order No",
        "Reason Description",
        "Reason Code",
        "Buyers DN No",
        "Buyers DN Date",
        "Credit Period",
        "Credit / Party Ledger",
        "Address 1",
        "Address 2",
        "Address 3",
        "Address 4",
        "State",
        "Place of Supply",
        "Country",
        "GSTIN",
        "GST Registration Type",
        "Debit Ledger 1",
        "Debit Ledger 1 Amount",
        "Debit Ledger 2",
        "Debit Ledger 2 Amount",
        "Debit Ledger 3",
        "Debit Ledger 3 Amount",
        "Debit Ledger 4",
        "Debit Ledger 4 Amount",
        "Debit Ledger 5",
        "Debit Ledger 5 Amount",
        "Debit Ledger 6",
        "Debit Ledger 6 Amount",
        "Debit Ledger 7",
        "Debit Ledger 7 Amount",
        "Debit Ledger 8",
        "Debit Ledger 8 Amount",
        "Debit Ledger 9",
        "Debit Ledger 9 Amount",
        "Debit Ledger 10",
        "Debit Ledger 10 Amount",
        "Debit Ledger 11",
        "Debit Ledger 11 Amount",
        "Debit Ledger 12",
        "Debit Ledger 12 Amount",
        "Debit Ledger 13",
        "Debit Ledger 13 Amount",
        "Debit Ledger 14",
        "Debit Ledger 14 Amount",
        "Debit Ledger 15",
        "Debit Ledger 15 Amount",
        "Debit Ledger 16",
        "Debit Ledger 16 Amount",
        "Debit Ledger 17",
        "Debit Ledger 17 Amount",
        "Debit Ledger 18",
        "Debit Ledger 18 Amount",
        "Debit Ledger 19",
        "Debit Ledger 19 Amount",
        "Debit Ledger 20",
        "Debit Ledger 20 Amount",
        "Debit Ledger 21",
        "Debit Ledger 21 Amount",
        "Debit Ledger 22",
        "Debit Ledger 22 Amount",
        "Debit Ledger 23",
        "Debit Ledger 23 Amount",
        "Debit Ledger 24",
        "Debit Ledger 24 Amount",
        "Debit Ledger 25",
        "Debit Ledger 25 Amount",
        "Debit Ledger 26",
        "Debit Ledger 26 Amount",
        "Debit Ledger 27",
        "Debit Ledger 27 Amount",
        "Debit Ledger 28",
        "Debit Ledger 28 Amount",
        "Debit Ledger 29",
        "Debit Ledger 29 Amount",
        "Debit Ledger 30",
        "Debit Ledger 30 Amount",
        "Cost Center",
        "Narration",
    ]

    debitnote_without_inventory_payload = {}
    for key, value in data.items():
        if key in debitnote_without_inventory_fields:
            debitnote_without_inventory_payload[key] = value

    return json.dumps({"body": [debitnote_without_inventory_payload]})


def insert_creditnote_without_inventory_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], creditnote_without_inventory_template_url: str, logger: AirbyteLogger
):
    creditnote_without_inventory_template_key = "5"
    creditnote_without_inventory_headers = prepare_headers(config=config, template_key=creditnote_without_inventory_template_key)
    creditnote_without_inventory_payload = prepare_creditnote_without_inventory_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST",
            url=creditnote_without_inventory_template_url,
            data=creditnote_without_inventory_payload,
            headers=creditnote_without_inventory_headers,
        )
    except Exception as e:
        logger.error(f"request for credit note not successful, {e}")
        return

    if response.status_code == 200:
        logger.info("credit note successfully inserted into Tally")
    else:
        logger.info("credit note cannot be inserted into Tally")


# 10. Sales without inventory Template - Date format problem
def prepare_sales_without_inventory_payload(data: Dict[str, Any], logger: AirbyteLogger):
    """
    1. Debit / Party Ledger
    2. Credit Ledger 1 , 2 , and so on
    3. Cost Center
    """
    required_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "Debit / Party Ledger",
        "Credit Ledger 1",
        "Credit Ledger 1 Amount",
    ]

    for field in required_fields:
        if (field not in data) or (data[field] == ""):
            logger.error(f"Please provide {field} as it is required field.")
            return

    sales_without_inventory_fields = [
        "Date",
        "Voucher No",
        "Voucher Type",
        "IS Invoice",
        "Bill Wise Details",
        "Debit / Party Ledger",
        "Address 1",
        "Address 2",
        "Address 3",
        "Address 4",
        "Pincode",
        "State",
        "Place of Supply",
        "Country",
        "VAT Tin No",
        "CST No",
        "Service Tax No",
        "GSTIN",
        "GST Registration Type",
        "Consignee Name",
        "Consignee Add 1",
        "Consignee Add 2",
        "Consignee Add 3",
        "Consignee Add 4",
        "Consignee State",
        "Consignee Country",
        "Consignee Pincode",
        "Consignee GSTIN",
        "Credit Ledger 1",
        "Credit Ledger 1 Amount",
        "Ledger 1 Description",
        "Credit Ledger 2",
        "Credit Ledger 2 Amount",
        "Ledger 2 Description",
        "Credit Ledger 3",
        "Credit Ledger 3 Amount",
        "Ledger 3 Description",
        "Credit Ledger 4",
        "Credit Ledger 4 Amount",
        "Ledger 4 Description",
        "Credit Ledger 5",
        "Credit Ledger 5 Amount",
        "Ledger 5 Description",
        "Credit Ledger 6",
        "Credit Ledger 6 Amount",
        "Ledger 6 Description",
        "Credit Ledger 7",
        "Credit Ledger 7 Amount",
        "Ledger 7 Description",
        "Credit Ledger 8",
        "Credit Ledger 8 Amount",
        "Ledger 8 Description",
        "Credit Ledger 9",
        "Credit Ledger 9 Amount",
        "Ledger 9 Description",
        "Credit Ledger 10",
        "Credit Ledger 10 Amount",
        "Ledger 10 Description",
        "Credit Ledger 11",
        "Credit Ledger 11 Amount",
        "Ledger 11 Description",
        "Credit Ledger 12",
        "Credit Ledger 12 Amount",
        "Ledger 12 Description",
        "Credit Ledger 13",
        "Credit Ledger 13 Amount",
        "Ledger 13 Description",
        "Credit Ledger 14",
        "Credit Ledger 14 Amount",
        "Ledger 14 Description",
        "Credit Ledger 15",
        "Credit Ledger 15 Amount",
        "Ledger 15 Description",
        "Credit Ledger 16",
        "Credit Ledger 16 Amount",
        "Ledger 16 Description",
        "Credit Ledger 17",
        "Credit Ledger 17 Amount",
        "Ledger 17 Description",
        "Credit Ledger 18",
        "Credit Ledger 18 Amount",
        "Ledger 18 Description",
        "Credit Ledger 19",
        "Credit Ledger 19 Amount",
        "Ledger 19 Description",
        "Credit Ledger 20",
        "Credit Ledger 20 Amount",
        "Ledger 20 Description",
        "Credit Ledger 21",
        "Credit Ledger 21 Amount",
        "Ledger 21 Description",
        "Credit Ledger 22",
        "Credit Ledger 22 Amount",
        "Ledger 22 Description",
        "Credit Ledger 23",
        "Credit Ledger 23 Amount",
        "Ledger 23 Description",
        "Credit Ledger 24",
        "Credit Ledger 24 Amount",
        "Ledger 24 Description",
        "Credit Ledger 25",
        "Credit Ledger 25 Amount",
        "Ledger 25 Description",
        "Credit Ledger 26",
        "Credit Ledger 26 Amount",
        "Ledger 26 Description",
        "Credit Ledger 27",
        "Credit Ledger 27 Amount",
        "Ledger 27 Description",
        "Credit Ledger 28",
        "Credit Ledger 28 Amount",
        "Ledger 28 Description",
        "Credit Ledger 29",
        "Credit Ledger 29 Amount",
        "Ledger 29 Description",
        "Credit Ledger 30",
        "Credit Ledger 30 Amount",
        "Ledger 30 Description",
        "Credit Period",
        "Cost Center",
        "Narration",
        "IRN Ack No",
        "IRN Ack Date",
        "IRN No",
        "IRN Bill to Place",
        "IRN Ship to State",
    ]

    sales_without_inventory_payload = {}
    for key, value in data.items():
        if key in sales_without_inventory_fields:
            sales_without_inventory_payload[key] = value

    return json.dumps({"body": [sales_without_inventory_payload]})


def insert_sales_without_inventory_to_tally(
    config: Mapping[str, Any], data: Dict[str, Any], sales_without_inventory_template_url: str, logger: AirbyteLogger
):
    sales_without_inventory_template_key = "2"
    sales_without_inventory_headers = prepare_headers(config=config, template_key=sales_without_inventory_template_key)
    sales_without_inventory_payload = prepare_sales_without_inventory_payload(data=data, logger=logger)

    try:
        response = requests.request(
            method="POST",
            url=sales_without_inventory_template_url,
            data=sales_without_inventory_payload,
            headers=sales_without_inventory_headers,
        )
    except Exception as e:
        logger.error(f"request for sales without inventory not successful, {e}")
        return

    if response.status_code == 200:
        logger.info("sales without inventory successfully inserted into Tally")
    else:
        logger.info("sales without inventory cannot be inserted into Tally")
