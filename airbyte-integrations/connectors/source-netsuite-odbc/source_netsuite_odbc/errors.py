# Airbyte Errors that are shown to customers are prepended with AIRBYTE_
# Internal Netsuite Errors that are used for error message conversion are prepended with NETSUITE_
# Conversion pairs should be kept together

NETSUITE_DRIVER_NOT_FOUND_ERROR = "Can't open lib 'NetSuite ODBC Drivers 8.1' : file not found"
AIRBYTE_ODBC_DRIVER_DOES_NOT_EXIST_ERROR = """Cannot connect to ODBC Driver because Driver does not exist.  If you're self hosting, 
  please install the correct linux driver.  If you're using the cloud version, please contact Airbyte Support"""


NETSUITE_INCORRECT_PASSWORD = "Failed to login using TBA"
AIRBYTE_ODBC_DRIVER_INCORRECT_PASSWORD_ERROR = """We failed to login using TBA.  This typically happens due to an incorrect ODBC password due
 an incorrect config.  Please check that your config is accurate."""