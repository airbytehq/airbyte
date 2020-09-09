import psycopg2
import sys
import json
import argparse

parser = argparse.ArgumentParser(description='Check if the provided creds can be used to successfully connect to the target postgres DB')
parser.add_argument("config_path")
try:
    args = parser.parse_args()
    config_path = args.config_path
    with open(config_path, 'r') as config_string:
        config_json = json.loads(config_string.read())
        conn = psycopg2.connect(
            "dbname='{postgres_database}' user='{postgres_username}' host='{postgres_host}' password='{postgres_password}' port='{postgres_port}'".format(**config_json))
except Exception as e:
    print(e)
    sys.exit(1)

sys.exit(0)
