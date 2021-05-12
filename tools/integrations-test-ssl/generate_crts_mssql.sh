#!/bin/bash

set -euo pipefail

openssl req -x509 -nodes -newkey rsa:2048 -subj '/CN=sqltest.airbyte.com' -keyout mssql.key -out mssql.pem
chmod 440 mssql.pem
chmod 440 mssql.key
