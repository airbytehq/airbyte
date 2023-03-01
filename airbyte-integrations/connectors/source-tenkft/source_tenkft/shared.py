#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os

import gspread
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.filedatalake import DataLakeFileClient, DataLakeServiceClient
from google.oauth2.service_account import Credentials

SECRET_CLIENT = None
AZURE_CREDENTIAL = None


def get_azure_credential() -> DefaultAzureCredential:
    global AZURE_CREDENTIAL
    if AZURE_CREDENTIAL is None:
        AZURE_CREDENTIAL = DefaultAzureCredential(additionally_allowed_tenants=["*"], exclude_shared_token_cache_credential=True)
    return AZURE_CREDENTIAL


def get_vault_secret_client() -> SecretClient:
    global SECRET_CLIENT
    if SECRET_CLIENT is None:
        logging.info("Initializing Vault Client")
        azure_credential = get_azure_credential()
        vault_url = os.environ["vault_url"]
        SECRET_CLIENT = SecretClient(vault_url=vault_url, credential=azure_credential)
        logging.info("Created Vault Client")
    return SECRET_CLIENT
