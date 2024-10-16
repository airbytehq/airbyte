import botocore.exceptions
import boto3
import mysql.connector
from mysql.connector import Error
import logging


from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import urlparse, parse_qs

from .constants import ADVERTISERS_QUERY, SHOPIFY_ACCESS_TOKEN_PATH

class AWSClient:
    def __init__(self, config: Mapping[str, Any]): 
        self.logger = logging.getLogger("airbyte")
        region_name: str = "us-east-1"
        env = config.get("env", "local")
        self.sid = SHOPIFY_ACCESS_TOKEN_PATH.format(account_id=config.get("secret_manager_account"))
        
        if env == "local":
            self.session = boto3.Session(
                aws_access_key_id=config.get('aws_access_key_id'),
                aws_secret_access_key=config.get('aws_secret_access_key'),
                aws_session_token=config.get('aws_session_token'),
                region_name=region_name
            )
            self.sid = self.sid.replace("{env}", "prod")
        else:
            self.session = boto3.Session(region_name=region_name)
            self.sid = self.sid.replace("{env}", env)
        
        self.secrets_manager_client = self.session.client('secretsmanager')

    def _get_shopify_token(self, shopify_id: str) -> Optional[str]:
        try:
            sid = self.sid.replace("{shop_id}",shopify_id)
            resp = self.secrets_manager_client.get_secret_value(SecretId=sid)
            return resp["SecretString"]
        except botocore.exceptions.ClientError as exc:
            self.logger.error(
                f"shopify: failed to get access token for active shop_id: {shopify_id} ({exc}). Shop will be excluded from the sync."
            )
            return None

class DatabaseClient:
    def __init__(self, config: Mapping[str, Any]):
        self.connection = self.create_connection(config)
        self.logger = logging.getLogger("airbyte")
    
    def extract_db_info(self, db_uri):
        parsed_uri = urlparse(db_uri)
        # Extract the components
        db_info = {
            'scheme': parsed_uri.scheme,  
            'username': parsed_uri.username,
            'password': parsed_uri.password,
            'host': parsed_uri.hostname,
            'port': parsed_uri.port,
            'database': parsed_uri.path[1:],  
            'query_params': parse_qs(parsed_uri.query)
        }
        return db_info
    
    def create_connection(self, config: Mapping[str, Any]):
        db_uri = config.get("db_uri", "")
        if not db_uri:
            raise Exception("Please pass in a DB_URI for Milk and Honey DB")
        
        db_info = self.extract_db_info(db_uri)
        try:
            connection =mysql.connector.connect(
                host = db_info['host'],     
                user = db_info['username'], 
                password = db_info['password'], 
                database = db_info['database'], 
                )
            return connection
        except Error as e:
            self.logger.error(f"Error while attempting to connecting to Milk and Honey DB: {e}")
            return None
        
    def _get_shopify_store_info(self):
        try:
            if self.connection.is_connected():
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(ADVERTISERS_QUERY)
                results = cursor.fetchall()
                self.logger.info("Fetched %d stores from Milk and Honey DB", len(results))
                return results
            else:
                raise Exception("Could not connect to Milk and Honey DB.")

        except Error as e:
            self.logger.error(f"Error executing query: {e}")

        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()
    
    