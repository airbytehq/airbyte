/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.performance;

import com.fasterxml.jackson.core.JsonProcessingException;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class Main {

  public static void main(final String[] args) {
    log.info("performance harness");
    try {
      final PerformanceTest test = new PerformanceTest(
          "airbyte/source-postgres:dev",
          """
              {
                  "ssl": false,
                  "host": "34.106.53.173",
                  "port": 5432,
                  "schemas": [
                      "10m_users"
                  ],
                  "database": "performance",
                  "password": "$Y'>3TI='{|Fl\\"')",
                  "ssl_mode": {
                      "mode": "disable"
                  },
                  "username": "postgres",
                  "tunnel_method": {
                      "tunnel_method": "NO_TUNNEL"
                  },
                  "replication_method": {
                      "method": "Standard"
                  }
              }
           """,
          """
   {
  "streams": [
    {
      "stream": {
        "name": "purchases",
        "namespace": "10m_users",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "user_id": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "product_id": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "returned_at": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            },
            "purchased_at": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            },
            "added_to_cart_at": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            }
          }
        },
        "default_cursor_field": [],
        "supported_sync_modes": [
          "full_refresh",
          "incremental"
        ],
        "source_defined_primary_key": [
          [
            "id"
          ]
        ]
      },
      "sync_mode": "full_refresh",
      "primary_key": [
        [
          "id"
        ]
      ],
      "cursor_field": [
        "id"
      ],
      "destination_sync_mode": "append"
    },
    {
      "stream": {
        "name": "users",
        "namespace": "10m_users",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "age": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "name": {
              "type": "string"
            },
            "email": {
              "type": "string"
            },
            "title": {
              "type": "string"
            },
            "gender": {
              "type": "string"
            },
            "height": {
              "type": "number"
            },
            "weight": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "language": {
              "type": "string"
            },
            "telephone": {
              "type": "string"
            },
            "blood_type": {
              "type": "string"
            },
            "created_at": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            },
            "occupation": {
              "type": "string"
            },
            "updated_at": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            },
            "nationality": {
              "type": "string"
            },
            "academic_degree": {
              "type": "string"
            }
          }
        },
        "default_cursor_field": [],
        "supported_sync_modes": [
          "full_refresh",
          "incremental"
        ],
        "source_defined_primary_key": [
          [
            "id"
          ]
        ]
      },
      "sync_mode": "full_refresh",
      "primary_key": [
        [
          "id"
        ]
      ],
      "cursor_field": [
        "updated_at"
      ],
      "destination_sync_mode": "append"
    },
    {
      "stream": {
        "name": "products",
        "namespace": "10m_users",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {
              "type": "number",
              "airbyte_type": "integer"
            },
            "make": {
              "type": "string"
            },
            "year": {
              "type": "string"
            },
            "model": {
              "type": "string"
            },
            "price": {
              "type": "number"
            },
            "created_at": {
              "type": "string",
              "format": "date-time",
              "airbyte_type": "timestamp_with_timezone"
            }
          }
        },
        "default_cursor_field": [],
        "supported_sync_modes": [
          "full_refresh",
          "incremental"
        ],
        "source_defined_primary_key": [
          [
            "id"
          ]
        ]
      },
      "sync_mode": "full_refresh",
      "primary_key": [
        [
          "id"
        ]
      ],
      "cursor_field": [
        "created_at"
      ],
      "destination_sync_mode": "append"
    }
  ]
}
              """);
      test.runTest();
//      test.dirtyStart();
    } catch (final Exception e) {
      throw new RuntimeException(e);

    }
    System.exit(1);
  }

}
