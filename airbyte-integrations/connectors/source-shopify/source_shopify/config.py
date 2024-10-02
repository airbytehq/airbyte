import botocore.exceptions
import boto3
import mysql.connector
from mysql.connector import Error


from typing import Any, List, Mapping
from urllib.parse import urlparse, parse_qs

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from .auth import MissingAccessTokenError, ShopifyAuthenticator
from .errors import DownloaderError
from .constants import ADVERTISERS_QUERY, SHOPIFY_ACCESS_TOKEN_PATH

class ConfigCreator:
    
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
            '''
            if self.env == 'prod':
                session = boto3.session.Session()
            else:
                session = boto3.session.Session(profile_name='rewardstyledev')

            '''
            session = boto3.Session(aws_access_key_id=aws_credentials['aws_access_key_id'], 
                                    aws_secret_access_key=aws_credentials['aws_secret_access_key'], 
                                    aws_session_token=aws_credentials['aws_session_token'], 
                                    region_name="us-east-1")

            client = session.client("secretsmanager")
            sid = SHOPIFY_ACCESS_TOKEN_PATH.format(shopify_id)
            resp = client.get_secret_value(SecretId=sid)

            return resp["SecretString"]
        except botocore.exceptions.ClientError as exc:
            print(
                f"shopify: failed to get access token for active shop_id: {shopify_id} ({exc}). Shop will be excluded from the sync."
            )
            return None

    def _get_shopy_store_info(self):
        try:
            connection = mysql.connector.connect(
                host = self.db_info['host'],     
                user = self.db_info['username'], 
                password = self.db_info['password'], 
                database = self.db_info['database'], 
                )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute(ADVERTISERS_QUERY)
                results = cursor.fetchall()

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
        shopify_stores = self._get_shopy_store_info()
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
        return shops

class LTKShopifyConfigCreator:
    """
    Gather all the LTK shopify stores
    """
    cfg = ConfigCreator()
    migrate_key: str = "shops"

    @classmethod
    def modify_config(cls, config: Mapping[str, Any], source: Source = None) -> Mapping[str, Any]:
        aws_credentials = {"aws_access_key_id": config['aws_access_key_id'],
                           "aws_secret_access_key": config['aws_secret_access_key'],
                           "aws_session_token": config['aws_session_token']}
        env = config.get('env', 'local')
        config[cls.migrate_key] = cls.cfg.gatherShopifyStores(config['db_uri'], env, aws_credentials)
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.modify_config(config, source)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config


    @classmethod
    def adjustConfig(cls, args: List[str], source: Source) -> None:
        """
        This method checks the input args, should the config be migrated,
        transform if neccessary and emit the CONTROL message.
        """
        # get config path
        config_path = AirbyteEntrypoint(source).extract_config(args)
        # proceed only if `--config` arg is provided
        if config_path:
            # read the existing config
            config = source.read_config(config_path)
            cls.modify_and_save(config_path, source, config)
    