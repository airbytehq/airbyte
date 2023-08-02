/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeDestinationResolver.getNumberOfFileBuffers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoopTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption.KeyType;
import io.airbyte.integrations.destination.s3.EncryptionConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StagingDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeS3StagingDestination.class);
  private final String airbyteEnvironment;

  public SnowflakeS3StagingDestination(final String airbyteEnvironment) {
    this(new SnowflakeSQLNameTransformer(), airbyteEnvironment);
  }

  public SnowflakeS3StagingDestination(final SnowflakeSQLNameTransformer nameTransformer, final String airbyteEnvironment) {
    super("", nameTransformer, new SnowflakeSqlOperations());
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final S3DestinationConfig s3Config = getS3DestinationConfig(config);
    final EncryptionConfig encryptionConfig = EncryptionConfig.fromJson(config.get("loading_method").get("encryption"));
    if (!isPurgeStagingData(config) && encryptionConfig instanceof AesCbcEnvelopeEncryption c && c.keyType() == KeyType.EPHEMERAL) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(
              "You cannot use ephemeral keys and disable purging your staging data. This would produce S3 objects that you cannot decrypt.");
    }
    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final SnowflakeS3StagingSqlOperations snowflakeS3StagingSqlOperations =
        new SnowflakeS3StagingSqlOperations(nameTransformer, s3Config.getS3Client(), s3Config, encryptionConfig);
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = super.getNamingResolver().getIdentifier(config.get("schema").asText());
      attemptTableOperations(outputSchema, database, nameTransformer, snowflakeS3StagingSqlOperations,
          true);
      attemptStageOperations(outputSchema, database, nameTransformer, snowflakeS3StagingSqlOperations);
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

  private static void attemptStageOperations(final String outputSchema,
                                             final JdbcDatabase database,
                                             final NamingConventionTransformer namingResolver,
                                             final SnowflakeS3StagingSqlOperations sqlOperations)
      throws Exception {

    // verify we have permissions to create/drop stage
    final String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID());
    final String stageName = sqlOperations.getStageName(outputSchema, outputTableName);
    sqlOperations.createStageIfNotExists(database, stageName);

    // try to make test write to make sure we have required role
    try {
      sqlOperations.attemptWriteToStage(outputSchema, stageName, database);
    } finally {
      // drop created tmp stage
      sqlOperations.dropStageIfExists(database, stageName);
    }
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
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final S3DestinationConfig s3Config = getS3DestinationConfig(config);
    final EncryptionConfig encryptionConfig = EncryptionConfig.fromJson(config.get("loading_method").get("encryption"));

    SnowflakeSqlGenerator sqlGenerator = new SnowflakeSqlGenerator();
    ParsedCatalog parsedCatalog = new CatalogParser(sqlGenerator).parseCatalog(catalog);
    TyperDeduper typerDeduper;
    if (TypingAndDedupingFlag.isDestinationV2()) {
      typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, new SnowflakeDestinationHandler(getDatabase(getDataSource(config))), parsedCatalog);
    } else {
      typerDeduper = new NoopTyperDeduper();
    }

    return new StagingConsumerFactory().create(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        new SnowflakeS3StagingSqlOperations(getNamingResolver(), s3Config.getS3Client(), s3Config, encryptionConfig),
        getNamingResolver(),
        CsvSerializedBuffer.createFunction(null, () -> new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX, getNumberOfFileBuffers(config))),
        config,
        catalog,
        isPurgeStagingData(config),
        new TypeAndDedupeOperationValve(),
        typerDeduper,
        parsedCatalog);
  }

  private S3DestinationConfig getS3DestinationConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get("loading_method");
    return S3DestinationConfig.getS3DestinationConfig(loadingMethod);
  }

  public static boolean isPurgeStagingData(final JsonNode config) {
    final JsonNode loadingMethod = config.get("loading_method");
    if (!loadingMethod.has("purge_staging_data")) {
      return true;
    } else {
      return loadingMethod.get("purge_staging_data").asBoolean();
    }
  }

}
