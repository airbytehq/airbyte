#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import io
import os
import time
import json
import zipfile
import requests
import xmltodict
import subprocess
import xml.etree.ElementTree as ET
from google.cloud import secretmanager
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple


class MeliInvoices(HttpStream):

    url_base = "http://api.mercadolibre.com/"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.credstash_key = config["credstash_key"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.year_month = config["year_month"]
        self.google_project_id = config["google_project_id"]
        self.google_secret_aws_credstash_credentials = config["google_secret_aws_credstash_credentials"]
        self.aws_access_key_id = config["aws_access_key_id"]
        self.aws_secret_access_key = config["aws_secret_access_key"]
        self.access_token = self.get_access_token()
    
    def get_access_token(self):
        # Meli URL to get the access_token
        url = "https://api.mercadolibre.com/oauth/token"
        # Build the parent name from the project.
        # parent = f"projects/{project_id}"

        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()

        # # Create the parent secret.
        # secret = client.create_secret(
        #     request={
        #         "parent": parent,
        #         "secret_id": secret_id,
        #         "secret": {"replication": {"automatic": {}}},
        #     }
        # )
        # # Add the secret version.
        # version = client.add_secret_version(
        #     request={"parent": secret.name, "payload": {"data": b"hello world!"}}
        # )

        # Getting ACCESS_KEY_ID
        resource_name = f"projects/{self.google_project_id}/secrets/{self.google_secret_aws_credstash_credentials}"
        response = client.access_secret_version(name=resource_name)
        aws_credentials = response.payload.data.decode('UTF-8')
        print(aws_credentials)
        logger.info(aws_credentials)


        # Getting the credentials from Secrets Manager
        aws_access_key_id = self.aws_access_key_id
        aws_secret_access_key = self.aws_secret_access_key
        
        bash_command = "chmod 777 -R ./bash"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        bash_command = f"./bash/configure_aws_credentials.sh {aws_access_key_id} {aws_secret_access_key}"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

        bash_command = f"credstash get {self.credstash_key}"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        refresh_token = output.decode('utf-8').strip()
        print(type(refresh_token))
        print(refresh_token)

        payload = json.dumps({
            "grant_type":"refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "client_secret": self.client_secret
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        access_token = response.json()["access_token"] 
        new_refresh_token = response.json()["refresh_token"]

        if new_refresh_token != refresh_token:
            # Updating Credstash
            # Example: credstash -r us-east-1 put -k {self.refresh_token} 'devpass_updated' role=dev -a
            bash_command = f"credstash put {self.credstash_key} {new_refresh_token}"
            process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

        # Response 403, token not valid anymore 
        
        # check se o que recebemos é igual ao do response
        # retry to generate the access_token
        # Credstash (Policy on AWS)
        # KMS
        # Dynamo tem o secret e o public
        # KMS tem o private e o public
        # Salvar no container criptografada e descriptografar com o secret manager
        # Ninguém pode ler lá
        # Public key, como usar o Secret Manager
        # Install merama core

        # Pegar com o secret manager
        # Colocar na env variables
        # Instalar merama Core (CredentialStorage)
        # 


        logger.info(f"Access Token: {access_token}")
        logger.info(f"Access Token: {new_refresh_token}")
        return access_token

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        # return f"users/{self.client_id}/invoices/sites/MLB/batch_request/period/stream?start={self.start_date}&end={self.end_date}"
        return f"users/{self.client_id}/invoices/sites/MLB/batch_request/period/{self.year_month}"
    
    def request_headers(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Mapping[str, Any]:
        """
        Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {'Authorization': f'Bearer {self.access_token}'}
    
    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):

        logger.info("Parsing Response")

        logger.info("Saving XML files locally")
        zfile = zipfile.ZipFile(io.BytesIO(response.content))
        zfile.extractall()
        time.sleep(10)

        path_meli = './emitidas_mercado_livre/xml'
        path_outro_erp = './emitidas_outro_erp/xml'
        paths = [path_meli, path_outro_erp]

        logger.info("Iterating through the xml folders to unify all xmls in just one object")
        items = []
        for path in paths:
            for filename in os.listdir(path):
                if not filename.endswith('.xml'): continue
                fullname = os.path.join(path, filename)
                tree = ET.parse(fullname)
            
                # Trasforming XML in string
                root = tree.getroot()
                xml = ET.tostring(root)

                # Transforming XML in json
                xml = xmltodict.parse(xml)
                items.append(xml)

        # with open('./invoices.json', 'w+') as f:
        #     json.dump(items, f)
        #     f.truncate()
        # ns0:nfeProc
        # ns0:procEventoNFe

        return items


class SourceMeliFull(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()

        return [
            MeliInvoices(authenticator=auth, config=config)
        ]
