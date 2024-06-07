/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import org.junit.jupiter.api.Order;

@Order(3)
@edu.umd.cs.findbugs.annotations.SuppressWarnings(value = "NP_NULL_ON_SOME_PATH")
class MySqlSslJdbcSourceAcceptanceTest extends MySqlJdbcSourceAcceptanceTest {

  @Override
  protected JsonNode config() {
    return testdb.testConfigBuilder()
        .with(JdbcUtils.SSL_KEY, true)
        .build();
  }

  @Override
  protected MySQLTestDatabase createTestDatabase() {
    return new MySQLTestDatabase(new MySQLContainerFactory().shared("mysql:8.0"))
        .withConnectionProperty("useSSL", "true")
        .withConnectionProperty("requireSSL", "true")
        .initialized()
        .with("SHOW STATUS LIKE 'Ssl_cipher'");
  }

}
