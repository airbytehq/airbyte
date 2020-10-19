"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import psycopg2
import sys
import json
import argparse

parser = argparse.ArgumentParser(description='Check if the provided creds can be used to successfully connect to the target postgres DB')
parser.add_argument("--config", "-c", help="Path to the config.json file containing the DB creds")
parser.add_argument("--discover", nargs='?', const='')

try:
    args = parser.parse_args()
    config_path = args.config
    with open(config_path, 'r') as config_string:
        config_json = json.loads(config_string.read())
        conn = psycopg2.connect(
            "dbname='{postgres_database}' user='{postgres_username}' host='{postgres_host}' password='{postgres_password}' port='{postgres_port}'".format(
                **config_json))
except Exception as e:
    print(e)
    sys.exit(1)

# If connection check is successful write a fake catalog for the discovery worker to find
with open("catalog.json", "w") as catalog:
    catalog.write('{"streams":[]}')

sys.exit(0)
