import botocore.exceptions
import boto3
import mysql.connector
from mysql.connector import Error
import logging


from typing import Any, List, Mapping
from urllib.parse import urlparse, parse_qs

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from .auth import MissingAccessTokenError, ShopifyAuthenticator
from .constants import ADVERTISERS_QUERY, SHOPIFY_ACCESS_TOKEN_PATH

class ConfigCreator:
    logger = logging.getLogger("airbyte")
    
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


    def _get_shopify_token(self, shopify_id: str, aws_credentials: dict) -> str:
        try:
            if self.env == "local":
                session = boto3.Session(aws_access_key_id=aws_credentials['aws_access_key_id'], 
                                        aws_secret_access_key=aws_credentials['aws_secret_access_key'], 
                                        aws_session_token=aws_credentials['aws_session_token'], 
                                        region_name="us-east-1")
                sid = SHOPIFY_ACCESS_TOKEN_PATH.format("prod", shopify_id)
            else:
                session = boto3.session.Session(region_name="us-east-1")

            client = session.client("secretsmanager")
            sid = SHOPIFY_ACCESS_TOKEN_PATH.format(self.env, shopify_id)
            resp = client.get_secret_value(SecretId=sid)

            return resp["SecretString"]
        except botocore.exceptions.ClientError as exc:
            print(
                f"shopify: failed to get access token for active shop_id: {shopify_id} ({exc}). Shop will be excluded from the sync."
            )
            return None

    def _get_shopify_store_info(self):
        connection = None
        try:
            connection =mysql.connector.connect(
                host = self.db_info['host'],     
                user = self.db_info['username'], 
                password = self.db_info['password'], 
                database = self.db_info['database'], 
                )

            if connection and connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute(ADVERTISERS_QUERY)
                results = cursor.fetchall()
                self.logger.info("Fetched %d stores from Milk and Honey", len(results))

                return results

        except Error as e:
            print(f"Error executing query: {e}")

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def gatherShopifyStores(self, db_uri, env, aws_credentials):
        self.db_info = self.extract_db_info(db_uri)
        self.env = env
        shops = []
        shopify_stores = self._get_shopify_store_info()
        if not shopify_stores:
            raise Exception("No Shopify Store data available in Milk And Honey.")

        for row in shopify_stores:
            shop_config = {}
            shop_name = row['advertiser_homepage'].replace("https://", "")
            shop_name = shop_name.replace('.myshopify.com', "")
            shop_config['shop'] = shop_name
            shop_config['shop_id'] = row['affiliateId']
            api_password = self._get_shopify_token(row['affiliateId'], aws_credentials)
            shop_config["credentials"] =  {"auth_method": "api_password", 
                                           "api_password": api_password}
            if not api_password: 
                print(f"shopify: failed to get access token for active shop: {shop_name}. It will be excluded from the sync.")
                continue
            shops.append(shop_config)
        self.logger.info("Fetched %d well-formed (M&H +  SecretManager) stores from Milk and Honey for extraction", len(shops))
        return shops
    