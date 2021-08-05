#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import json

import pytest


@pytest.fixture
def mssql_spec_schema():
    return json.loads(
        """
    {
  "documentationUrl": "https://docs.airbyte.io/integrations/destinations/mssql",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MSSQL Source Spec",
    "type": "object",
    "required": ["host", "port", "database", "username"],
    "additionalProperties": false,
    "properties": {
      "host": {
        "description": "Hostname of the database.",
        "type": "string"
      },
      "port": {
        "description": "Port of the database.",
        "type": "integer",
        "minimum": 0,
        "maximum": 65536,
        "examples": ["1433"]
      },
      "database": {
        "description": "Name of the database.",
        "type": "string",
        "examples": ["master"]
      },
      "username": {
        "description": "Username to use to access the database.",
        "type": "string"
      },
      "password": {
        "description": "Password associated with the username.",
        "type": "string",
        "airbyte_secret": true
      },
      "ssl_method": {
        "title": "SSL Method",
        "type": "object",
        "description": "Encryption method to use when communicating with the database",
        "order": 6,
        "oneOf": [
          {
            "title": "Unencrypted",
            "additionalProperties": false,
            "description": "Data transfer will not be encrypted.",
            "required": ["ssl_method"],
            "properties": {
              "ssl_method": {
                "type": "string",
                "const": "unencrypted",
                "enum": ["unencrypted"],
                "default": "unencrypted"
              }
            }
          },
          {
            "title": "Encrypted (trust server certificate)",
            "additionalProperties": false,
            "description": "Use the cert provided by the server without verification.  (For testing purposes only!)",
            "required": ["ssl_method"],
            "properties": {
              "ssl_method": {
                "type": "string",
                "const": "encrypted_trust_server_certificate",
                "enum": ["encrypted_trust_server_certificate"],
                "default": "encrypted_trust_server_certificate"
              }
            }
          },
          {
            "title": "Encrypted (verify certificate)",
            "additionalProperties": false,
            "description": "Verify and use the cert provided by the server.",
            "required": ["ssl_method", "trustStoreName", "trustStorePassword"],
            "properties": {
              "ssl_method": {
                "type": "string",
                "const": "encrypted_verify_certificate",
                "enum": ["encrypted_verify_certificate"],
                "default": "encrypted_verify_certificate"
              },
              "hostNameInCertificate": {
                "title": "Host Name In Certificate",
                "type": "string",
                "description": "Specifies the host name of the server. The value of this property must match the subject property of the certificate.",
                "order": 7
              }
            }
          }
        ]
      },
      "replication_method": {
        "type": "string",
        "title": "Replication Method",
        "description": "Replication method to use for extracting data from the database. STANDARD replication requires no setup on the DB side but will not be able to represent deletions incrementally. CDC uses {TBC} to detect inserts, updates, and deletes. This needs to be configured on the source database itself.",
        "default": "STANDARD",
        "enum": ["STANDARD", "CDC"]
      }
    }
  }
}
    """
    ).get("connectionSpecification")


@pytest.fixture
def postgres_source_spec_schema():
    return json.loads(
        """
    {
  "documentationUrl": "https://docs.airbyte.io/integrations/sources/postgres",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Postgres Source Spec",
    "type": "object",
    "required": ["host", "port", "database", "username"],
    "additionalProperties": false,
    "properties": {
      "host": {
        "title": "Host",
        "description": "Hostname of the database.",
        "type": "string",
        "order": 0
      },
      "port": {
        "title": "Port",
        "description": "Port of the database.",
        "type": "integer",
        "minimum": 0,
        "maximum": 65536,
        "default": 5432,
        "examples": ["5432"],
        "order": 1
      },
      "database": {
        "title": "DB Name",
        "description": "Name of the database.",
        "type": "string",
        "order": 2
      },
      "username": {
        "title": "User",
        "description": "Username to use to access the database.",
        "type": "string",
        "order": 3
      },
      "password": {
        "title": "Password",
        "description": "Password associated with the username.",
        "type": "string",
        "airbyte_secret": true,
        "order": 4
      },
      "ssl": {
        "title": "Connect using SSL",
        "description": "Encrypt client/server communications for increased security.",
        "type": "boolean",
        "default": false,
        "order": 5
      },
      "replication_method": {
        "type": "object",
        "title": "Replication Method",
        "description": "Replication method to use for extracting data from the database.",
        "order": 6,
        "oneOf": [
          {
            "title": "Standard",
            "additionalProperties": false,
            "description": "Standard replication requires no setup on the DB side but will not be able to represent deletions incrementally.",
            "required": ["method"],
            "properties": {
              "method": {
                "type": "string",
                "const": "Standard",
                "enum": ["Standard"],
                "default": "Standard",
                "order": 0
              }
            }
          },
          {
            "title": "Logical Replication (CDC)",
            "additionalProperties": false,
            "description": "Logical replication uses the Postgres write-ahead log (WAL) to detect inserts, updates, and deletes. This needs to be configured on the source database itself. Only available on Postgres 10 and above. Read the <a href=https://docs.airbyte.io/integrations/sources/postgres>Postgres Source</a> docs for more information.",
            "required": ["method", "replication_slot", "publication"],
            "properties": {
              "method": {
                "type": "string",
                "const": "CDC",
                "enum": ["CDC"],
                "default": "CDC",
                "order": 0
              },
              "replication_slot": {
                "type": "string",
                "description": "A pgoutput logical replication slot.",
                "order": 1
              },
              "publication": {
                "type": "string",
                "description": "A Postgres publication used for consuming changes.",
                "order": 2
              }
            }
          }
        ]
      }
    }
  }
}
"""
    ).get("connectionSpecification")
