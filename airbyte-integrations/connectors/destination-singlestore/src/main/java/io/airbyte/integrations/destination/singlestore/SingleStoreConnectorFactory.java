/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.parseJdbcParameters;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import java.time.Duration;
import java.util.Map;
import javax.sql.DataSource;
import org.jetbrains.annotations.NotNull;

public final class SingleStoreConnectorFactory {

  private static final String SINGLE_STORE_METRIC_NAME = "Airbyte Destination Connector";
  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of("allowLocalInfile", "true");
  static final Map<String, String> DEFAULT_SSL_JDBC_PARAMETERS = MoreMaps.merge(ImmutableMap.of("sslMode", "trust"), DEFAULT_JDBC_PARAMETERS);

  private SingleStoreConnectorFactory() {}

  public static DataSource createDataSource(JsonNode config) {
    final String jdbcUrl = String.format("jdbc:singlestore://%s:%s/%s?_connector_name=%s", config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(), config.get(JdbcUtils.DATABASE_KEY).asText(), SINGLE_STORE_METRIC_NAME);
    final ImmutableMap.Builder<Object, Object> configBuilder =
        ImmutableMap.builder().put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText()).put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);
    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }
    var jdbcConfig = Jsons.jsonNode(configBuilder.build());
    var connectionProperties = MoreMaps.merge(parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY), getDefaultConnectionProperties(config));
    var builder =
        new DataSourceFactory.DataSourceBuilder(
            jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
            jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
            DatabaseDriver.SINGLESTORE.getDriverClassName(),
            jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
                .withConnectionProperties(connectionProperties);
    if (connectionProperties.get("connectTimeout") != null) {
      builder.withConnectionTimeout(Duration.ofMillis(Long.parseLong(connectionProperties.get("connectTimeout"))));
    }
    return modifyDataSourceBuilder(builder).build();
  }

  private static Map<String, String> getDefaultConnectionProperties(@NotNull JsonNode config) {
    if (JdbcUtils.useSsl(config)) {
      return DEFAULT_SSL_JDBC_PARAMETERS;
    } else {
      return DEFAULT_JDBC_PARAMETERS;
    }
  }

  private static DataSourceFactory.DataSourceBuilder modifyDataSourceBuilder(@NotNull DataSourceFactory.DataSourceBuilder builder) {
    return builder.withConnectionTimeout(Duration.ofSeconds(60))
        .withConnectionInitSql("""
                               CREATE OR REPLACE FUNCTION can_cast(v VARCHAR(254), t VARCHAR(30)) RETURNS BOOL AS
                                 DECLARE
                                   v_pat VARCHAR(255) = CONCAT(v, "%");
                                 BEGIN
                                   IF v is NULL OR t = 'varchar' THEN
                                     RETURN TRUE;
                                   ELSIF t = 'bigint' THEN
                                     RETURN v !:> BIGINT !:> VARCHAR(255) = REPLACE(v, ' ', '');
                                   ELSIF t = 'date' THEN
                                     RETURN v !:> DATE !:> VARCHAR(255) = REPLACE(v, ' ', '');
                                   ELSIF t = 'timestamp' THEN
                                     RETURN v !:> TIMESTAMP(6) !:> VARCHAR(255) LIKE REGEXP_REPLACE(REPLACE(v_pat, 'T', ' '), 'z|Z', '');
                                   ELSIF t = 'time' THEN
                                     RETURN v !:> TIME(6) !:> VARCHAR(255) LIKE v_pat;
                                   ELSIF t = 'json' THEN
                                     RETURN (v:> VARCHAR(255) = '') OR (v !:> JSON IS NOT NULL);
                                   ELSIF t = 'decimal' THEN
                                     RETURN (v !:> DECIMAL(38, 9) !:> VARCHAR(255)) LIKE v_pat;
                                   ELSIF t = 'boolean' THEN
                                     RETURN UCASE(v) = 'TRUE' OR UCASE(v) = 'FALSE';
                                   ELSE
                                     RETURN FALSE;
                                   END IF;
                                 END
                               """);
  }

}
