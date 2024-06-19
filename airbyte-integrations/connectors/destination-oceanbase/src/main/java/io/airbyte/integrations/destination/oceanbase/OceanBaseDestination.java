/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
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
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

public class OceanBaseDestination extends AbstractJdbcDestination<MinimumDestinationState> implements Destination {
  
  private static final Logger LOGGER = LoggerFactory.getLogger(OceanBaseDestination.class);

  public static final String DRIVER_CLASS = "com.oceanbase.jdbc.Driver";
  public static final String URL_FORMAT_STRING = "jdbc:oceanbase://%s:%s";

  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of(
          "zeroDateTimeBehavior", "convertToNull",
          "allowLoadLocalInfile", "true");

  static final Map<String, String> DEFAULT_SSL_JDBC_PARAMETERS = MoreMaps.merge(ImmutableMap.of(
                  "useSSL", "true",
                  "requireSSL", "true",
                  "verifyServerCertificate", "false"),
          DEFAULT_JDBC_PARAMETERS);

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
      return DEFAULT_SSL_JDBC_PARAMETERS;
    } else {
      return DEFAULT_JDBC_PARAMETERS;
    }
  }

  @NotNull
  @Override
  public JsonNode toJdbcConfig(@NotNull final JsonNode config) {
    final String connectionString = String.format(URL_FORMAT_STRING,
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asText());

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
  protected JdbcSqlGenerator getSqlGenerator() {
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


  public static void main(final String[] args) throws Exception {
    final Destination destination = sshWrappedDestination();
    LOGGER.info("starting destination: {}", OceanBaseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", OceanBaseDestination.class);
  }

}
