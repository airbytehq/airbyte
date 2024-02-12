/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteRecordMessage;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.NoopTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoopV2TableMigrator;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcDestination extends JdbcConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcDestination.class);

  public static final String RAW_SCHEMA_OVERRIDE = "raw_data_schema";

  public static final String DISABLE_TYPE_DEDUPE = "disable_type_dedupe";

  private final NamingConventionTransformer namingResolver;
  private final SqlOperations sqlOperations;

  protected NamingConventionTransformer getNamingResolver() {
    return namingResolver;
  }

  protected SqlOperations getSqlOperations() {
    return sqlOperations;
  }

  public AbstractJdbcDestination(final String driverClass,
                                 final NamingConventionTransformer namingResolver,
                                 final SqlOperations sqlOperations) {
    super(driverClass);
    this.namingResolver = namingResolver;
    this.sqlOperations = sqlOperations;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);

    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.SCHEMA_KEY).asText());
      attemptTableOperations(outputSchema, database, namingResolver, sqlOperations, false);
      if (TypingAndDedupingFlag.isDestinationV2()) {
        final var v2RawSchema = namingResolver.getIdentifier(TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE)
            .orElse(JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE));
        attemptTableOperations(v2RawSchema, database, namingResolver, sqlOperations, false);
        destinationSpecificTableOperations(database);
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final ConnectionErrorException ex) {
      final String message = getErrorMessage(ex.getStateCode(), ex.getErrorCode(), ex.getExceptionMessage(), ex);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(ex, message);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(message);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  /**
   * Specific Databases may have additional checks unique to them which they need to perform, override
   * this method to add additional checks.
   *
   * @param database the database to run checks against
   * @throws Exception
   */
  protected void destinationSpecificTableOperations(final JdbcDatabase database) throws Exception {}

  /**
   * This method is deprecated. It verifies table creation, but not insert right to a newly created
   * table. Use attemptTableOperations with the attemptInsert argument instead.
   */
  @Deprecated
  public static void attemptSQLCreateAndDropTableOperations(final String outputSchema,
                                                            final JdbcDatabase database,
                                                            final NamingConventionTransformer namingResolver,
                                                            final SqlOperations sqlOps)
      throws Exception {
    attemptTableOperations(outputSchema, database, namingResolver, sqlOps, false);
  }

  /**
   * Verifies if provided creds has enough permissions. Steps are: 1. Create schema if not exists. 2.
   * Create test table. 3. Insert dummy record to newly created table if "attemptInsert" set to true.
   * 4. Delete table created on step 2.
   *
   * @param outputSchema - schema to tests against.
   * @param database - database to tests against.
   * @param namingResolver - naming resolver.
   * @param sqlOps - SqlOperations object
   * @param attemptInsert - set true if need to make attempt to insert dummy records to newly created
   *        table. Set false to skip insert step.
   */
  public static void attemptTableOperations(final String outputSchema,
                                            final JdbcDatabase database,
                                            final NamingConventionTransformer namingResolver,
                                            final SqlOperations sqlOps,
                                            final boolean attemptInsert)
      throws Exception {
    // verify we have write permissions on the target schema by creating a table with a random name,
    // then dropping that table
    try {
      // Get metadata from the database to see whether connection is possible
      database.bufferedResultSetQuery(conn -> conn.getMetaData().getCatalogs(), JdbcUtils.getDefaultSourceOperations()::rowToJson);

      // verify we have write permissions on the target schema by creating a table with a random name,
      // then dropping that table
      final String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", ""));
      sqlOps.createSchemaIfNotExists(database, outputSchema);
      sqlOps.createTableIfNotExists(database, outputSchema, outputTableName);
      // verify if user has permission to make SQL INSERT queries
      try {
        if (attemptInsert) {
          sqlOps.insertRecords(database, List.of(getDummyRecord()), outputSchema, outputTableName);
        }
      } finally {
        sqlOps.dropTableIfExists(database, outputSchema, outputTableName);
      }
    } catch (final SQLException e) {
      if (Objects.isNull(e.getCause()) || !(e.getCause() instanceof SQLException)) {
        throw new ConnectionErrorException(e.getSQLState(), e.getErrorCode(), e.getMessage(), e);
      } else {
        final SQLException cause = (SQLException) e.getCause();
        throw new ConnectionErrorException(e.getSQLState(), cause.getErrorCode(), cause.getMessage(), e);
      }
    } catch (final Exception e) {
      throw new Exception(e);
    }
  }

  /**
   * Generates a dummy AirbyteRecordMessage with random values.
   *
   * @return AirbyteRecordMessage object with dummy values that may be used to test insert permission.
   */
  private static PartialAirbyteMessage getDummyRecord() {
    final JsonNode dummyDataToInsert = Jsons.deserialize("{ \"field1\": true }");
    return new PartialAirbyteMessage()
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream("stream1")
            .withEmittedAt(1602637589000L))
        .withSerialized(dummyDataToInsert.toString());
  }

  /**
   * Subclasses which need to modify the DataSource should override
   * {@link #modifyDataSourceBuilder(DataSourceFactory.DataSourceBuilder)} rather than this method.
   */
  @VisibleForTesting
  public DataSource getDataSource(final JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);
    final Map<String, String> connectionProperties = getConnectionProperties(config);
    final DataSourceFactory.DataSourceBuilder builder = new DataSourceFactory.DataSourceBuilder(
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClassName,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
            .withConnectionProperties(connectionProperties)
            .withConnectionTimeout(getConnectionTimeout(connectionProperties));
    return modifyDataSourceBuilder(builder).build();
  }

  protected DataSourceFactory.DataSourceBuilder modifyDataSourceBuilder(final DataSourceFactory.DataSourceBuilder builder) {
    return builder;
  }

  @VisibleForTesting
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  protected Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY);
    final Map<String, String> defaultProperties = getDefaultConnectionProperties(config);
    assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  private void assertCustomParametersDontOverwriteDefaultParameters(final Map<String, String> customParameters,
                                                                    final Map<String, String> defaultParameters) {
    for (final String key : defaultParameters.keySet()) {
      if (customParameters.containsKey(key) && !Objects.equals(customParameters.get(key), defaultParameters.get(key))) {
        throw new IllegalArgumentException("Cannot overwrite default JDBC parameter " + key);
      }
    }
  }

  protected abstract Map<String, String> getDefaultConnectionProperties(final JsonNode config);

  public abstract JsonNode toJdbcConfig(JsonNode config);

  protected abstract JdbcSqlGenerator getSqlGenerator();

  protected JdbcDestinationHandler getDestinationHandler(final String databaseName, final JdbcDatabase database) {
    return new JdbcDestinationHandler(databaseName, database);
  }

  /**
   * "database" key at root of the config json, for any other variants in config, override this
   * method.
   *
   * @param config
   * @return
   */
  protected String getDatabaseName(final JsonNode config) {
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    throw new NotImplementedException("Should use the getSerializedMessageConsumer instead");
  }

  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    final DataSource dataSource = getDataSource(config);
    final JdbcDatabase database = getDatabase(dataSource);
    if (TypingAndDedupingFlag.isDestinationV2()) {
      // TODO: This logic exists in all V2 destinations.
      // This is sad that if we forget to add this, there will be a null pointer during parseCatalog
      final String defaultNamespace = config.get("schema").asText();
      for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
        if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
          stream.getStream().setNamespace(defaultNamespace);
        }
      }
      final JdbcSqlGenerator sqlGenerator = getSqlGenerator();
      final ParsedCatalog parsedCatalog = TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE)
          .map(override -> new CatalogParser(sqlGenerator, override))
          .orElse(new CatalogParser(sqlGenerator))
          .parseCatalog(catalog);
      final String databaseName = getDatabaseName(config);
      final var migrator = new JdbcV1V2Migrator(namingResolver, database, databaseName);
      final NoopV2TableMigrator v2TableMigrator = new NoopV2TableMigrator();
      final DestinationHandler<TableDefinition> destinationHandler = getDestinationHandler(databaseName, database);
      final boolean disableTypeDedupe = config.has(DISABLE_TYPE_DEDUPE) && config.get(DISABLE_TYPE_DEDUPE).asBoolean(false);
      final TyperDeduper typerDeduper;
      if (disableTypeDedupe) {
        typerDeduper = new NoOpTyperDeduperWithV1V2Migrations<>(sqlGenerator, destinationHandler, parsedCatalog, migrator, v2TableMigrator,
            8);
      } else {
        typerDeduper =
            new DefaultTyperDeduper<>(sqlGenerator, destinationHandler, parsedCatalog, migrator, v2TableMigrator, 8);
      }
      return JdbcBufferedConsumerFactory.createAsync(
          outputRecordCollector,
          database,
          sqlOperations,
          namingResolver,
          config,
          catalog,
          defaultNamespace,
          typerDeduper);
    }
    return JdbcBufferedConsumerFactory.createAsync(
        outputRecordCollector,
        database,
        sqlOperations,
        namingResolver,
        config,
        catalog,
        null,
        new NoopTyperDeduper());
  }

}
