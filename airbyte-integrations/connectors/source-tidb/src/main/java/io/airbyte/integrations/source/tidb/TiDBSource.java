/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TiDBSource extends AbstractJdbcSource<MysqlType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(TiDBSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  static final String DRIVER_CLASS = DatabaseDriver.MYSQL.getDriverClassName();
  public static final List<String> SSL_PARAMETERS = List.of(
      "useSSL=true",
      "requireSSL=true",
      "verifyServerCertificate=false");

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new TiDBSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public TiDBSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new TiDBSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asInt(),
        config.get(JdbcUtils.DATABASE_KEY).asText()));

    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null
        && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText()).append("&");
    }

    // only if config ssl and ssl == true, use ssl to connect db
    if (config.has(JdbcUtils.SSL_KEY) && config.get(JdbcUtils.SSL_KEY).asBoolean()) {
      jdbcUrl.append(String.join("&", SSL_PARAMETERS)).append("&");
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "information_schema",
        "metrics_schema",
        "performance_schema",
        "mysql");
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = TiDBSource.sshWrappedSource();
    LOGGER.info("starting source: {}", TiDBSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", TiDBSource.class);
  }

}
