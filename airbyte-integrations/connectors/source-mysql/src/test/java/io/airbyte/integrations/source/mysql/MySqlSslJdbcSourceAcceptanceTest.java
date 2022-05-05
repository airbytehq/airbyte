/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.MySqlSource.SSL_PARAMETERS;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.BeforeEach;

class MySqlSslJdbcSourceAcceptanceTest extends MySqlJdbcSourceAcceptanceTest {

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", Strings.addRandomSuffix("db", "_", 10))
        .put("username", TEST_USER)
        .put("password", TEST_PASSWORD.call())
        .put("ssl", true)
        .build());

    try (final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s/%s?%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText(),
            String.join("&", SSL_PARAMETERS)), SQLDialect.MYSQL)) {
      database = new Database(dslContext);

      database.query(ctx -> {
        ctx.fetch("CREATE DATABASE " + config.get("database").asText());
        ctx.fetch("SHOW STATUS LIKE 'Ssl_cipher'");
        return null;
      });
    }

    super.setup();
  }

}
