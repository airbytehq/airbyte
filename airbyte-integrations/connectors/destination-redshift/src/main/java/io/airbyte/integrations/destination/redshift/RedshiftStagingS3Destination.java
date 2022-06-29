/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.JDBC_URL;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.PASSWORD;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.SSL_JDBC_PARAMETERS;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.USERNAME;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.getJdbcConfig;
import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.findS3Options;
import static io.airbyte.integrations.destination.s3.S3DestinationConfig.getS3DestinationConfig;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.redshift.operations.RedshiftS3StagingSqlOperations;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption.KeyType;
import io.airbyte.integrations.destination.s3.EncryptionConfig;
import io.airbyte.integrations.destination.s3.NoEncryption;
import io.airbyte.integrations.destination.s3.S3Destination;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStagingS3Destination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStagingS3Destination.class);

  public RedshiftStagingS3Destination() {
    super(RedshiftInsertDestination.DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations());
  }

  private boolean isEphemeralKeysAndPurgingStagingData(JsonNode config, EncryptionConfig encryptionConfig) {
    return !isPurgeStagingData(config) && encryptionConfig instanceof AesCbcEnvelopeEncryption c && c.keyType() == KeyType.EPHEMERAL;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final S3DestinationConfig s3Config = getS3DestinationConfig(findS3Options(config));
    final EncryptionConfig encryptionConfig = config.has("uploading_method") ?
        EncryptionConfig.fromJson(config.get("uploading_method").get("encryption")) : new NoEncryption();
    if (isEphemeralKeysAndPurgingStagingData(config, encryptionConfig)) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(
              "You cannot use ephemeral keys and disable purging your staging data. This would produce S3 objects that you cannot decrypt.");
    }
    S3Destination.attemptS3WriteAndDelete(new S3StorageOperations(new RedshiftSQLNameTransformer(), s3Config.getS3Client(), s3Config), s3Config, s3Config.getBucketPath());

    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final RedshiftS3StagingSqlOperations redshiftS3StagingSqlOperations =
        new RedshiftS3StagingSqlOperations(nameTransformer, s3Config.getS3Client(), s3Config, encryptionConfig);
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);
      final String outputSchema = super.getNamingResolver().getIdentifier(config.get("schema").asText());
      AirbyteSentry.executeWithTracing("CreateAndDropTable",
          () -> attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, redshiftS3StagingSqlOperations));
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

  @Override
  public DataSource getDataSource(final JsonNode config) {
    final var jdbcConfig = getJdbcConfig(config);
    return DataSourceFactory.create(
        jdbcConfig.get(USERNAME).asText(),
        jdbcConfig.has(PASSWORD) ? jdbcConfig.get(PASSWORD).asText() : null,
        RedshiftInsertDestination.DRIVER_CLASS,
        jdbcConfig.get(JDBC_URL).asText(),
        SSL_JDBC_PARAMETERS);
  }

  @Override
  protected NamingConventionTransformer getNamingResolver() {
    return new RedshiftSQLNameTransformer();
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return SSL_JDBC_PARAMETERS;
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
    final EncryptionConfig encryptionConfig = config.has("uploading_method") ?
        EncryptionConfig.fromJson(config.get("uploading_method").get("encryption")) : new NoEncryption();
    final JsonNode s3Options = findS3Options(config);
    final S3DestinationConfig s3Config = getS3DestinationConfig(s3Options);
    return new StagingConsumerFactory().create(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        new RedshiftS3StagingSqlOperations(getNamingResolver(), s3Config.getS3Client(), s3Config, encryptionConfig),
        getNamingResolver(),
        CsvSerializedBuffer.createFunction(null, () -> new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX)),
        config,
        catalog,
        isPurgeStagingData(s3Options));
  }

  private boolean isPurgeStagingData(final JsonNode config) {
    return !config.has("purge_staging_data") || config.get("purge_staging_data").asBoolean();
  }

}
