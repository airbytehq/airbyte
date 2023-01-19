/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

class SnowflakeDataSourceUtilsTest {

  private final String config = """
                                {
                                  "host": "host",
                                  "role": "role",
                                  "schema": "SOURCE_SCHEMA",
                                  "database": "DATABASE",
                                  "warehouse": "WAREHOUSE",
                                  "credentials": {
                                    "auth_type": "OAuth",
                                    "client_id": "someid",
                                    "access_token": "**********",
                                    "client_secret": "clientSecret",
                                    "refresh_token": "token"
                                  }
                                }
                                """;
  private final String expectedJdbcUrl =
      "jdbc:snowflake://host/?role=role&warehouse=WAREHOUSE&database=DATABASE"
          + "&JDBC_QUERY_RESULT_FORMAT=JSON&CLIENT_SESSION_KEEP_ALIVE=true&application=airbyte_oss"
          + "&schema=SOURCE_SCHEMA&CLIENT_METADATA_REQUEST_USE_CONNECTION_CTX=true";

  @Test
  void testBuildJDBCUrl() {
    final JsonNode expectedConfig = Jsons.deserialize(config);

    final String jdbcURL = SnowflakeDataSourceUtils.buildJDBCUrl(expectedConfig, SnowflakeDataSourceUtils.AIRBYTE_OSS);

    assertEquals(expectedJdbcUrl, jdbcURL);
  }

  @Test
  void testBuildJDBCUrlWithParams() {
    final JsonNode expectedConfig = Jsons.deserialize(config);
    final String params = "someParameter1&param2=someParameter2";
    ((ObjectNode) expectedConfig).put("jdbc_url_params", params);

    final String jdbcURL = SnowflakeDataSourceUtils.buildJDBCUrl(expectedConfig, SnowflakeDataSourceUtils.AIRBYTE_OSS);

    assertEquals(expectedJdbcUrl + "&" + params, jdbcURL);
  }

}
