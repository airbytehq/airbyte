/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Databases;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.BeforeEach;

class MySqlSSLJdbcSourceAcceptanceTest extends MySqlJdbcSourceAcceptanceTest {

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", Strings.addRandomSuffix("db", "_", 10))
        .put("username", TEST_USER)
        .put("password", TEST_PASSWORD)
        .put("ssl", true)
        .build());

    database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s?useSSL=true&requireSSL=true",
            config.get("host").asText(),
            config.get("port").asText()),
        MySqlSource.DRIVER_CLASS,

        SQLDialect.MYSQL);

    database.query(ctx -> {
      ctx.fetch("CREATE DATABASE " + config.get("database").asText());
      ctx.fetch("SHOW STATUS LIKE 'Ssl_cipher'");
      return null;
    });
    database.close();

    super.setup();
  }

}
