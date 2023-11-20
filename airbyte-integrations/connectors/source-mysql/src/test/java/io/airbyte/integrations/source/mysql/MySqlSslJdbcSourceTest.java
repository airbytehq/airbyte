/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.MySqlSource.SSL_PARAMETERS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import java.util.Map;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Order;

@Order(3)
class MySqlSslJdbcSourceTest extends MySqlJdbcSourceTest {

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
