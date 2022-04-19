/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.redshift.RedshiftSource;

public class RedshiftSslSourceAcceptanceTest extends RedshiftSourceAcceptanceTest {

  protected static JdbcDatabase createDatabase(final JsonNode config) {
    return Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:redshift://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        RedshiftSource.DRIVER_CLASS,
        "ssl=true;" +
            "sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
  }

}
