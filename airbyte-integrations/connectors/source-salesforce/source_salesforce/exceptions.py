#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys
from airbyte_cdk.logger import AirbyteLogger


class Error(Exception):
    """Base Error class for other exceptions"""
    # Define the instance of the Native Airbyte Logger
    logger = AirbyteLogger()


class SalesforceException(Exception):
    """
    Default Salesforce exception.
    """


class TypeSalesforceException(SalesforceException):
    """
    We use this exception for unknown input data types for Salesforce.
    """
    

class TmpFileIOError(Error):
    def __init__(self, msg: str, err: str = None):
        super().__init__(self.logger.fatal(f"{msg} for job: {msg}. Error: {err}"))
        
