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
      "jdbc:snowflake://host/?role=role&warehouse=WAREHOUSE&database=DATABASE&schema=SOURCE_SCHEMA&JDBC_QUERY_RESULT_FORMAT=JSON&CLIENT_SESSION_KEEP_ALIVE=true";

  @Test
  void testBuildJDBCUrl() {
    JsonNode expectedConfig = Jsons.deserialize(config);

    String jdbcURL = SnowflakeDataSourceUtils.buildJDBCUrl(expectedConfig);

    assertEquals(expectedJdbcUrl, jdbcURL);
  }

  @Test
  void testBuildJDBCUrlWithParams() {
    JsonNode expectedConfig = Jsons.deserialize(config);
    String params = "someParameter1&param2=someParameter2";
    ((ObjectNode) expectedConfig).put("jdbc_url_params", params);

    String jdbcURL = SnowflakeDataSourceUtils.buildJDBCUrl(expectedConfig);

    assertEquals(expectedJdbcUrl + "&" + params, jdbcURL);
  }

}
