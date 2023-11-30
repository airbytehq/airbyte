/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;

public class MySqlSslSourceAcceptanceTest extends MySqlSourceAcceptanceTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withStandardReplication()
        .withSsl(ImmutableMap.builder().put(JdbcUtils.MODE_KEY, "required").build())
        .build();
  }

}
