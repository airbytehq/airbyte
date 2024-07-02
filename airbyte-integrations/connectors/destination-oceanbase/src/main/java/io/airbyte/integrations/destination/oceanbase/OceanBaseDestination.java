/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.NoOpJdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.RawOnlySqlGenerator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.jetbrains.annotations.NotNull;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OceanBaseDestination extends AbstractJdbcDestination<MinimumDestinationState> implements Destination {

  private static final Logger LOG = LoggerFactory.getLogger(OceanBaseDestination.class);

  public static final String DRIVER_CLASS = "com.oceanbase.jdbc.Driver";
  public static final String URL_FORMAT_STRING = "jdbc:oceanbase://%s:%s/%s";

  public OceanBaseDestination() {
    super(DRIVER_CLASS, new OceanBaseNameTransformer(), new OceanBaseSqlOperations());
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new OceanBaseDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  @NotNull
  @Override
  protected Map<String, String> getDefaultConnectionProperties(@NotNull final JsonNode config) {
    if (JdbcUtils.useSsl(config)) {
      return ImmutableMap.of(
          "zeroDateTimeBehavior", "convertToNull",
          "allowLoadLocalInfile", "true",
          "useSSL", "true",
          "requireSSL", "true",
          "verifyServerCertificate", "false");
    } else {
      return ImmutableMap.of(
          "zeroDateTimeBehavior", "convertToNull",
          "allowLoadLocalInfile", "true");
    }
  }

  @NotNull
  @Override
  public JsonNode toJdbcConfig(@NotNull final JsonNode config) {
    final String connectionString = String.format(URL_FORMAT_STRING,
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, connectionString);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  @Override
  protected boolean shouldAlwaysDisableTypeDedupe() {
    return true;
  }

  @NotNull
  @Override
  protected JdbcSqlGenerator getSqlGenerator(JsonNode config) {
    return new RawOnlySqlGenerator(new OceanBaseNameTransformer());
  }

  @NotNull
  @Override
  protected JdbcDestinationHandler<MinimumDestinationState> getDestinationHandler(@NotNull final String databaseName,
                                                                                  @NotNull final JdbcDatabase database,
                                                                                  @NotNull final String rawTableSchema) {
    return new NoOpJdbcDestinationHandler<>(databaseName, database, rawTableSchema, SQLDialect.DEFAULT);
  }

  @NotNull
  @Override
  protected List<Migration<MinimumDestinationState>> getMigrations(@NotNull final JdbcDatabase database,
                                                                   @NotNull final String databaseName,
                                                                   @NotNull final SqlGenerator sqlGenerator,
                                                                   @NotNull final DestinationHandler<MinimumDestinationState> destinationHandler) {
    return List.of();
  }

  @NotNull
  @Override
  public DataSource getDataSource(@NotNull JsonNode config) {
    String url = String.format("jdbc:oceanbase://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    var hikariConfig = new HikariConfig();
    hikariConfig.setDriverClassName(DRIVER_CLASS);
    hikariConfig.setJdbcUrl(url);
    hikariConfig.setUsername(config.get(JdbcUtils.USERNAME_KEY).asText());
    hikariConfig.setPassword(config.get(JdbcUtils.PASSWORD_KEY).asText());
    hikariConfig.setInitializationFailTimeout(Integer.MIN_VALUE);
    hikariConfig.setAutoCommit(true);
    return new HikariDataSource(hikariConfig);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = sshWrappedDestination();
    LOG.info("starting destination: {}", OceanBaseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOG.info("completed destination: {}", OceanBaseDestination.class);
  }

}
