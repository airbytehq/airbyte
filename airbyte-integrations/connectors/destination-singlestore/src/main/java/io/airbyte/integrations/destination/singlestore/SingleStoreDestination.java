/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;
import static io.airbyte.cdk.integrations.util.ConfiguredCatalogUtilKt.addDefaultNamespaceToStreams;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.*;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.singlestore.typing_deduping.SingleStoreDestinationHandler;
import io.airbyte.integrations.destination.singlestore.typing_deduping.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreDestination extends AbstractJdbcDestination<MinimumDestinationState> implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreDestination.class);
  public static final String DRIVER_CLASS = DatabaseDriver.SINGLESTORE.getDriverClassName();
  private static final String SINGLE_STORE_METRIC_NAME = "Airbyte Destination Connector";
  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of("allowLocalInfile", "true");

  static final Map<String, String> DEFAULT_SSL_JDBC_PARAMETERS = MoreMaps.merge(ImmutableMap.of("sslMode", "trust"), DEFAULT_JDBC_PARAMETERS);

  public SingleStoreDestination() {
    super(DRIVER_CLASS, new SingleStoreNameTransformer(), new SingleStoreSqlOperations());
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new SingleStoreDestination();
    LOGGER.info("starting destination: {}", SingleStoreDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SingleStoreDestination.class);
  }

  @NotNull
  @Override
  protected DataSourceFactory.DataSourceBuilder modifyDataSourceBuilder(@NotNull DataSourceFactory.DataSourceBuilder builder) {
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

  @NotNull
  @Override
  protected Map<String, String> getDefaultConnectionProperties(@NotNull JsonNode config) {
    if (JdbcUtils.useSsl(config)) {
      return DEFAULT_SSL_JDBC_PARAMETERS;
    } else {
      return DEFAULT_JDBC_PARAMETERS;
    }
  }

  @NotNull
  @Override
  public JsonNode toJdbcConfig(@NotNull JsonNode config) {
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
    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final SingleStoreSqlOperations sqlOperations = (SingleStoreSqlOperations) getSqlOperations();
      final String outputSchema = getNamingResolver().getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      attemptTableOperations(outputSchema, database, getNamingResolver(), sqlOperations, false);
      sqlOperations.verifyLocalFileEnabled(database);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final ConnectionErrorException e) {
      final String message = getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage(message);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  @Nullable
  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(@NotNull JsonNode config,
                                                                       @NotNull ConfiguredAirbyteCatalog catalog,
                                                                       @NotNull Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    if (!TypingAndDedupingFlag.isDestinationV2()) {
      return super.getSerializedMessageConsumer(config, catalog, outputRecordCollector);
    }
    var database = getDatabase(getDataSource(config));
    var defaultNamespace = config.get(JdbcUtils.DATABASE_KEY).asText();
    if (!config.has(RAW_SCHEMA_OVERRIDE)) {
      // Set default raw_data_schema the same as database, because SingleStore doesn't support
      // cross-database transactions
      ((ObjectNode) config).put(RAW_SCHEMA_OVERRIDE, defaultNamespace);
    }
    addDefaultNamespaceToStreams(catalog, defaultNamespace);
    return getV2MessageConsumer(
        config,
        catalog,
        outputRecordCollector,
        database,
        defaultNamespace);
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  @NotNull
  @Override
  protected JdbcSqlGenerator getSqlGenerator(@NotNull JsonNode config) {
    return new SingleStoreSqlGenerator(getNamingResolver(), config);
  }

  @NotNull
  @Override
  protected JdbcDestinationHandler<MinimumDestinationState> getDestinationHandler(@NotNull String databaseName,
                                                                                  @NotNull JdbcDatabase database,
                                                                                  @NotNull String rawTableSchema) {
    return new SingleStoreDestinationHandler(databaseName, database, rawTableSchema);
  }

  @NotNull
  @Override
  protected List<Migration<MinimumDestinationState>> getMigrations(@NotNull JdbcDatabase database,
                                                                   @NotNull String databaseName,
                                                                   @NotNull SqlGenerator sqlGenerator,
                                                                   @NotNull DestinationHandler<MinimumDestinationState> destinationHandler) {
    return Collections.emptyList();
  }

}
