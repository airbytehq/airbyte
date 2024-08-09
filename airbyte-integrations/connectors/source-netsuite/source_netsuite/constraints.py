#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


# NETSUITTE REST API PATHS
REST_PATH: str = "/services/rest/"
RECORD_PATH: str = REST_PATH + "record/v1/"
META_PATH: str = RECORD_PATH + "metadata-catalog/"

# PREDEFINE REFERAL SCHEMA LINK, TEMPLATE
REFERAL_SCHEMA_URL: str = "/services/rest/record/v1/metadata-catalog/nsLink"
REFERAL_SCHEMA: dict = {
    "type": ["null", "object"],
    "properties": {
        "id": {"title": "Internal identifier", "type": ["string"]},
        "refName": {"title": "Reference Name", "type": ["null", "string"]},
        "externalId": {"title": "External identifier", "type": ["null", "string"]},
        "links": {
            "title": "Links",
            "type": "array",
            "readOnly": True,
        },
    },
}
# ELEMENTS TO REMOVE FROM SCHEMA
USLESS_SCHEMA_ELEMENTS: list = [
    "enum",
    "x-ns-filterable",
    "x-ns-custom-field",
    "nullable",
]

# PREDEFINE SCHEMA HEADER
SCHEMA_HEADERS: dict = {"Accept": "application/schema+json"}

# INCREMENTAL CURSOR FIELDS
INCREMENTAL_CURSOR: str = "lastModifiedDate"
CUSTOM_INCREMENTAL_CURSOR: str = "lastmodified"


NETSUITE_INPUT_DATE_FORMATS: list[str] = ["%m/%d/%Y", "%Y-%m-%d"]
NETSUITE_OUTPUT_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

# Custom SuiteQL queries
QUERY_CUSTOM_INVENTORY: str = "SELECT a.item AS ID, BUILTIN.DF(a.item) AS ItemName, i.description AS ItemDescription, c.preferredstocklevel, a.quantityavailable, c.preferredstocklevel - a.quantityavailable AS QuantityNeeded, a.quantityonorder, a.quantitycommitted, a.quantityavailable + a.quantityonorder AS QuantityAvailableAndOnOrder, ac.fullname AS ExpenseCogsAccount, a.quantityonhand, iil.quantityintransit, BUILTIN.DF(i.custitemiqffldproductfamily) AS ProductFamily FROM aggregateItemLocation a INNER JOIN item i ON a.item = i.id LEFT JOIN itemLocationConfiguration c ON c.location = a.location AND c.item = a.item LEFT JOIN account ac ON ac.id = i.expenseaccount LEFT JOIN inventoryItemLocations iil ON iil.item = a.item and iil.location = a.location WHERE a.location = 35 AND i.isinactive = 'F'"
QUERY_CUSTOM_SALES_ORDER: str = "SELECT t.id, trandate, t.status AS Status, BUILTIN.DF(tl.item) AS ItemName, i.fullname AS ItemFullName, i.description AS ItemDescription, i.weight AS Weight, ABS(tl.quantity) AS Quantity, tl.rate AS Rate, TO_CHAR(trandate, 'MM-Mon') AS Month, TO_CHAR(trandate, 'YYYY') AS Year, TO_CHAR(trandate, 'IW') AS Week, BUILTIN.DF(tl.class) AS Class, BUILTIN.DF(t.entity) AS Customer, BUILTIN.DF(tl.expenseaccount) AS ExpenseCogsAccount, TO_CHAR(t.lastModifiedDate, 'YYYY-MM-DD HH24:MI:SS.FF1') AS LastModifiedDate FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id INNER JOIN item i ON tl.item = i.id WHERE type = 'SalesOrd' AND trandate BETWEEN TO_DATE('{from_date}', 'YYYY-MM-DD') AND TO_DATE('{to_date}', 'YYYY-MM-DD') AND tl.mainline = 'F' AND tl.donotdisplayline <> 'T'"