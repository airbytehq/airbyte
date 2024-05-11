/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import java.time.Duration;
import org.junit.jupiter.api.Disabled;

@Disabled
public class RedshiftSslSourceAcceptanceTest extends RedshiftSourceAcceptanceTest {

  private static final Duration CONNECTION_TIMEOUT = Duration.ofSeconds(60);

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
                "sslfactory=com.amazon.redshift.ssl.NonValidatingFactory"),
            CONNECTION_TIMEOUT));
  }

}
