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
QUERY_CUSTOM_SALES_ORDER: str = "SELECT t.id as TranID, t.id || '-' || tl.linesequencenumber AS id, trandate, t.status AS Status, BUILTIN.DF(tl.item) AS ItemName, i.fullname AS ItemFullName, i.description AS ItemDescription, i.weight AS Weight, ABS(tl.quantity) AS Quantity, tl.rate AS Rate, TO_CHAR(trandate, 'MM-Mon') AS Month, TO_CHAR(trandate, 'YYYY') AS Year, TO_CHAR(trandate, 'IW') AS Week, BUILTIN.DF(tl.class) AS Class, BUILTIN.DF(t.entity) AS Customer, BUILTIN.DF(tl.expenseaccount) AS ExpenseCogsAccount, TO_CHAR(t.lastModifiedDate, 'YYYY-MM-DD HH24:MI:SS.FF1') AS LastModifiedDate FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id INNER JOIN item i ON tl.item = i.id WHERE type = 'SalesOrd' AND t.lastModifiedDate BETWEEN TO_DATE('{from_date}', 'YYYY-MM-DD') AND TO_DATE('{to_date}', 'YYYY-MM-DD') AND tl.mainline = 'F' AND tl.donotdisplayline <> 'T'"
QUERY_CUSTOM_PRODUCTION: str = "SELECT TO_CHAR(t.lastModifiedDate, 'YYYY-MM-DD HH24:MI:SS.FF1') AS LastModifiedDate, BUILTIN.DF(tl.entity) AS customer, t.id, t.number AS workordernumber, t.trandate, t.actualproductionstartdate, t.actualproductionenddate, i.itemid, i.description, tl.quantity AS qtyplanned, tl.quantityshiprecv AS qtyactual, t.status, BUILTIN.DF(t.status) AS statusdescription FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id INNER JOIN item i ON tl.item = i.id WHERE tl.mainline = 'T' AND i.itemid LIKE 'WH-%' AND t.type = 'WorkOrd' AND t.lastModifiedDate BETWEEN TO_DATE('{from_date}', 'YYYY-MM-DD') AND TO_DATE('{to_date}', 'YYYY-MM-DD')"
QUERY_CUSTOM_WHOLESALE: str = "SELECT ml.InternalId AS Id ,COALESCE(i.description, i.displayname, tl.memo, CASE WHEN tl.itemtype = 'ShipItem' THEN 'Shipping' ELSE NULL END) AS ItemName ,CASE WHEN (LOWER(COALESCE(i.description, i.displayname)) LIKE '%gift card%') OR tl.itemtype IN ('Discount', 'ShipItem') THEN NULL ELSE tl.netamount * -1 END AS SalesAmount ,CASE WHEN (LOWER(COALESCE(i.description, i.displayname)) LIKE '%gift card%') OR tl.itemtype IN ('Discount', 'ShipItem') THEN NULL ELSE tl.quantity * -1 END AS Quantity ,CASE WHEN tl.itemtype = 'ShipItem' THEN tl.rateamount ELSE NULL END AS ShippingCost ,CASE WHEN tl.itemtype = 'Discount' THEN tl.rateamount ELSE NULL END AS Discount ,tl.ItemType ,ml.TranDate ,ml.InternalId ,ml.DocumentNumber ,ml.CustomerName ,ml.CustomerInternalId ,ml.SalesRep ,tl.linesequencenumber AS LineIndex ,ml.OriginalSalesOrderInternalId ,BUILTIN.DF(tl.class) AS Class ,ml.Market ,ml.Segment FROM ( SELECT trandate AS TranDate ,t.id AS InternalId ,t.tranid AS DocumentNumber ,c.entitytitle AS CustomerName ,tl.entity AS CustomerInternalId ,e.entityid AS SalesRep ,tl.createdfrom AS OriginalSalesOrderInternalId ,BUILTIN.DF(c.custentity32) AS Market ,BUILTIN.DF(c.custentity33) AS Segment FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id LEFT JOIN customer c ON t.entity = c.id LEFT JOIN employee e ON c.salesrep = e.id WHERE tl.mainline = 'T' AND t.type IN ('CashRfnd', 'CashSale', 'CustCred', 'Deposit', 'CustInvc', 'Journal', 'CustPymt') AND BUILTIN.DF(tl.class) = '6 Wholesale' ) ml INNER JOIN transactionline tl ON tl.transaction = ml.InternalId AND tl.mainline = 'F' AND tl.donotdisplayline = 'F' AND tl.itemtype <> 'TaxGroup' AND (tl.itemtype <> 'ShipItem' OR tl.rateamount > 0) LEFT JOIN item i ON tl.item = i.id WHERE ml.trandate >= '1/1/2022' UNION SELECT t.id * 1000 AS Id ,COALESCE(i.description, i.displayname, tl.memo, CASE WHEN tl.itemtype = 'ShipItem' THEN 'Shipping' ELSE NULL END) AS ItemName ,CASE WHEN BUILTIN.DF(tal.account) = '40100 Bulk Coffee Sales' THEN debitforeignamount * -1 ELSE NULL END AS SalesAmount ,NULL AS Quantity ,NULL AS ShippingCost ,CASE WHEN BUILTIN.DF(tal.account) = '50500 Discounts Allowed' THEN tl.netamount * -1 ELSE NULL END AS Discount ,tl.ItemType ,t.trandate AS TranDate ,t.id AS InternalId ,t.tranid AS DocumentNumber ,c.entitytitle AS CustomerName ,tl.entity AS CustomerInternalId ,e.entityid AS SalesRep ,tl.linesequencenumber AS LineIndex ,tl.createdfrom AS OriginalSalesOrderInternalId ,BUILTIN.DF(tl.class) AS Class ,BUILTIN.DF(c.custentity32) AS Market ,BUILTIN.DF(c.custentity33) AS Segment FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id INNER JOIN transactionaccountingline tal ON tal.transaction = t.id AND tal.transactionline = tl.id AND tal.posting = 'T' LEFT JOIN customer c ON tl.entity = c.id LEFT JOIN employee e ON c.salesrep = e.id LEFT JOIN item i ON tl.item = i.id WHERE tl.mainline = 'T' AND t.type = 'Journal' AND BUILTIN.DF(tl.class) = '6 Wholesale' AND BUILTIN.DF(tal.account) IN ('40100 Bulk Coffee Sales', '50500 Discounts Allowed') AND t.trandate >= '1/1/2022' UNION SELECT t.id * 1000 AS Id ,COALESCE(i.description, i.displayname, tl.memo, CASE WHEN tl.itemtype = 'ShipItem' THEN 'Shipping' ELSE NULL END) AS ItemName ,CASE WHEN (LOWER(COALESCE(i.description, i.displayname)) LIKE '%gift card%') OR tl.itemtype IN ('Discount', 'ShipItem') THEN NULL ELSE tl.netamount * -1 END AS SalesAmount ,CASE WHEN (LOWER(COALESCE(i.description, i.displayname)) LIKE '%gift card%') OR tl.itemtype IN ('Discount', 'ShipItem') THEN NULL ELSE tl.quantity * -1 END AS Quantity ,CASE WHEN tl.itemtype = 'ShipItem' THEN tl.rateamount ELSE NULL END AS ShippingCost ,CASE WHEN tl.itemtype = 'Discount' THEN tl.rateamount ELSE NULL END AS Discount ,tl.ItemType ,t.trandate AS TranDate ,t.id AS InternalId ,t.tranid AS DocumentNumber ,c.entitytitle AS CustomerName ,tl.entity AS CustomerInternalId ,e.entityid AS SalesRep ,tl.linesequencenumber AS LineIndex ,tl.createdfrom AS OriginalSalesOrderInternalId ,BUILTIN.DF(tl.class) AS Class ,BUILTIN.DF(c.custentity32) AS Market ,BUILTIN.DF(c.custentity33) AS Segment FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id INNER JOIN transactionaccountingline tal ON tal.transaction = t.id AND tal.transactionline = tl.id AND tal.posting = 'T' LEFT JOIN customer c ON tl.entity = c.id LEFT JOIN employee e ON c.salesrep = e.id LEFT JOIN item i ON tl.item = i.id WHERE t.type = 'Deposit' AND BUILTIN.DF(tl.class) = '6 Wholesale' AND BUILTIN.DF(tal.account) = '40100 Bulk Coffee Sales' AND t.trandate >= '1/1/2022' UNION SELECT t.id * 1000 AS Id ,COALESCE(i.description, i.displayname, tl.memo, CASE WHEN tl.itemtype = 'ShipItem' THEN 'Shipping' ELSE NULL END) AS ItemName ,NULL AS SalesAmount ,NULL AS Quantity ,NULL ShippingCost ,CASE WHEN t.type = 'CustPymt' THEN tl.netamount * -1 ELSE tl.rateamount * -1 END AS Discount ,tl.ItemType ,t.trandate AS TranDate ,t.id AS InternalId ,t.tranid AS DocumentNumber ,c.entitytitle AS CustomerName ,tl.entity AS CustomerInternalId ,e.entityid AS SalesRep ,tl.linesequencenumber AS LineIndex ,tl.createdfrom AS OriginalSalesOrderInternalId ,BUILTIN.DF(tl.class) AS Class ,BUILTIN.DF(c.custentity32) AS Market ,BUILTIN.DF(c.custentity33) AS Segment FROM transaction t INNER JOIN transactionline tl ON tl.transaction = t.id INNER JOIN transactionaccountingline tal ON tal.transaction = t.id AND tal.transactionline = tl.id AND tal.posting = 'T' LEFT JOIN customer c ON tl.entity = c.id LEFT JOIN employee e ON c.salesrep = e.id LEFT JOIN item i ON tl.item = i.id WHERE t.type IN ('CustPymt', 'CustCred') AND BUILTIN.DF(tl.class) = '6 Wholesale' AND BUILTIN.DF(tal.account) = '50500 Discounts Allowed' AND t.trandate >= '1/1/2022'"
QUERY_CUSTOM_ITEM: str = "SELECT itemid, id, displayname, BUILTIN.DF(itemtype) AS ItemType FROM item"