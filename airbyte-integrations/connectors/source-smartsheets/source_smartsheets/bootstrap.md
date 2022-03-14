# Smartsheets
The Smartsheets Source Connector is written in Python and uses `smartsheet-python-sdk`.

### building the AirbyteRecord
It builds the JSON Schema from `Smartsheet.columns` objects, it makes a `dict` like `column_tite`: `column_value` for each row of of the sheet and passes each to an `AirbyteRecord`.

The construction of that dict uses a mapping of column IDs to column names to enforce matched key-value pairs.

### auth
The current implementation uses a basic client / access token auth strategy.

### sync modes
Full overwrite sync mode assumed given restrictions on Smartsheet size.

### rate limiting
Rate limiting is 300 requests per minute, which I've not hit in developement / regular use of the connector. 
