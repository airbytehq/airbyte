/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;

public class RedshiftSslSourceAcceptanceTest extends RedshiftSourceAcceptanceTest {

  @Override
  protected JdbcDatabase createDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.REDSHIFT.getDriverClassName(),
            String.format(DatabaseDriver.REDSHIFT.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()),
            JdbcUtils.parseJdbcParameters("ssl=true&" +
                "sslfactory=com.amazon.redshift.ssl.NonValidatingFactory")));
  }

}
