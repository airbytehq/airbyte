/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts.AIRBYTE_CLOUD;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.destination.snowflake.SnowflakeBulkLoadDestination.InvalidValueException;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV2TableMigrator;
import io.airbyte.protocol.models.v0.*;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeBulkLoadDestination extends AbstractJdbcDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeBulkLoadDestination.class);
  private static final String PROPERTIES = "properties";
  public static final String TUNNEL_METHOD = "tunnel_method";
  public static final String NO_TUNNEL = "NO_TUNNEL";
  public static final String SSL_MODE = "ssl_mode";
  public static final String MODE = "mode";
  public static final String SSL_MODE_ALLOW = "allow";
  public static final String SSL_MODE_PREFER = "prefer";
  public static final String SSL_MODE_DISABLE = "disable";

  private static final String RAW_SCHEMA_OVERRIDE = "raw_data_schema";
  private static final String BULK_LOAD_FILE_FORMAT = "bulk_load_file_format";
  private static final String BULK_LOAD_S3_STAGES = "bulk_load_s3_stages";

  private final String airbyteEnvironment;

  public SnowflakeBulkLoadDestination() {
    this(new SnowflakeSQLNameTransformer());
  }

  public SnowflakeBulkLoadDestination(final NamingConventionTransformer nameTransformer) {
    super("", nameTransformer, new SnowflakeBulkLoadSqlOperations(nameTransformer, "", ""));
    this.airbyteEnvironment = AIRBYTE_CLOUD;
  }

  public SnowflakeBulkLoadDestination(final NamingConventionTransformer nameTransformer, final String airbyteEnvironment) {
    super("", nameTransformer, new SnowflakeBulkLoadSqlOperations(nameTransformer, "", ""));
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final SnowflakeBulkLoadSqlOperations snowflakeBulkLoadSqlOperations = new SnowflakeBulkLoadSqlOperations(nameTransformer, "", "");
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = nameTransformer.getIdentifier(config.get("schema").asText());
      attemptTableOperations(outputSchema, database, nameTransformer,
          snowflakeBulkLoadSqlOperations, true);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new SnowflakeBulkLoadDestination();
    LOGGER.info("starting destination: {}", SnowflakeBulkLoadDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SnowflakeBulkLoadDestination.class);
  }

  public static class StageNotFoundException extends Exception {

    public StageNotFoundException(String message) {
      super(message);
    }

  }

  public static class InvalidValueException extends Exception {

    public InvalidValueException(String message) {
      super(message);
    }

  }

  public static String findMatchingStageName(Map<String, String> s3StageMap, String s3Path) throws StageNotFoundException {
    for (Map.Entry<String, String> entry : s3StageMap.entrySet()) {
      if (s3Path.startsWith(entry.getValue())) {
        return entry.getKey();
      }
    }
    throw new StageNotFoundException("No matching Snowflake stage name found for S3 path: " + s3Path);
  }

  public static String getRelativePath(String rootPath, String fullS3Path) throws InvalidValueException {
    if (fullS3Path.startsWith(rootPath)) {
      return fullS3Path.substring(rootPath.length());
    }
    throw new InvalidValueException("S3 path " + fullS3Path + " does not start with root path " + rootPath);
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config, airbyteEnvironment);
  }

  @Override
  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector) {
    final String defaultNamespace = config.get("schema").asText();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().setNamespace(defaultNamespace);
      }
    }

    final SnowflakeSqlGenerator sqlGenerator = new SnowflakeSqlGenerator();
    final ParsedCatalog parsedCatalog;
    final TyperDeduper typerDeduper;
    final JdbcDatabase database = getDatabase(getDataSource(config));
    final String databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final SnowflakeDestinationHandler snowflakeDestinationHandler = new SnowflakeDestinationHandler(databaseName, database);
    final CatalogParser catalogParser;
    if (TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent()) {
      catalogParser = new CatalogParser(sqlGenerator, TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get());
    } else {
      catalogParser = new CatalogParser(sqlGenerator);
    }
    parsedCatalog = catalogParser.parseCatalog(catalog);
    final SnowflakeV1V2Migrator migrator = new SnowflakeV1V2Migrator(getNamingResolver(), database, databaseName);
    final SnowflakeV2TableMigrator v2TableMigrator = new SnowflakeV2TableMigrator(database, databaseName, sqlGenerator, snowflakeDestinationHandler);
    typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, snowflakeDestinationHandler, parsedCatalog, migrator, v2TableMigrator, 8);

    return new StagingConsumerFactory().createAsync(
        outputRecordCollector,
        database,
        new SnowflakeBulkLoadSqlOperations(getNamingResolver(),
                                           config.get(BULK_LOAD_FILE_FORMAT).asText(),
                                           config.get(BULK_LOAD_S3_STAGES).asText()),
        getNamingResolver(),
        config,
        catalog,
        true,
        new TypeAndDedupeOperationValve(),
        typerDeduper,
        parsedCatalog,
        defaultNamespace,
        true,
        Optional.of(getSnowflakeBufferMemoryLimit()));
  }

  private static long getSnowflakeBufferMemoryLimit() {
    return (long) (Runtime.getRuntime().maxMemory() * 0.5);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog, Consumer<AirbyteMessage> outputRecordCollector) {
    return (AirbyteMessageConsumer) getSerializedMessageConsumer(config, catalog, outputRecordCollector);
  }

}
