/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.integrations.base.errors.messages.ErrorMessage.getErrorMessage;
import static io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.UPLOADING_METHOD;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.SSL_JDBC_PARAMETERS;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.getJdbcConfig;
import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.findS3Options;
import static io.airbyte.integrations.destination.s3.S3DestinationConfig.getS3DestinationConfig;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.redshift.operations.RedshiftS3StagingSqlOperations;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption.KeyType;
import io.airbyte.integrations.destination.s3.EncryptionConfig;
import io.airbyte.integrations.destination.s3.NoEncryption;
import io.airbyte.integrations.destination.s3.S3BaseChecks;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
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

  private boolean isEphemeralKeysAndPurgingStagingData(final JsonNode config, final EncryptionConfig encryptionConfig) {
    return !isPurgeStagingData(config) && encryptionConfig instanceof AesCbcEnvelopeEncryption c && c.keyType() == KeyType.EPHEMERAL;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final S3DestinationConfig s3Config = getS3DestinationConfig(findS3Options(config));
    final EncryptionConfig encryptionConfig =
        config.has(UPLOADING_METHOD) ? EncryptionConfig.fromJson(config.get(UPLOADING_METHOD).get(JdbcUtils.ENCRYPTION_KEY)) : new NoEncryption();
    if (isEphemeralKeysAndPurgingStagingData(config, encryptionConfig)) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(
              "You cannot use ephemeral keys and disable purging your staging data. This would produce S3 objects that you cannot decrypt.");
    }
    S3BaseChecks.attemptS3WriteAndDelete(new S3StorageOperations(new RedshiftSQLNameTransformer(), s3Config.getS3Client(), s3Config), s3Config,
        s3Config.getBucketPath());

    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final RedshiftS3StagingSqlOperations redshiftS3StagingSqlOperations =
        new RedshiftS3StagingSqlOperations(nameTransformer, s3Config.getS3Client(), s3Config, encryptionConfig);
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);
      final String outputSchema = super.getNamingResolver().getIdentifier(config.get(JdbcUtils.SCHEMA_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, redshiftS3StagingSqlOperations);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final ConnectionErrorException e) {
      final String message = getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(message);
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
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        RedshiftInsertDestination.DRIVER_CLASS,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
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
    final EncryptionConfig encryptionConfig =
        config.has(UPLOADING_METHOD) ?
            EncryptionConfig.fromJson(config.get(UPLOADING_METHOD).get(JdbcUtils.ENCRYPTION_KEY)) : new NoEncryption();
    final JsonNode s3Options = findS3Options(config);
    final S3DestinationConfig s3Config = getS3DestinationConfig(s3Options);
    final int numberOfFileBuffers = getNumberOfFileBuffers(s3Options);

    if (numberOfFileBuffers > FileBuffer.SOFT_CAP_CONCURRENT_STREAM_IN_BUFFER) {
      LOGGER.warn("""
                  Increasing the number of file buffers past {} can lead to increased performance but
                  leads to increased memory usage. If the number of file buffers exceeds the number
                  of streams {} this will create more buffers than necessary, leading to nonexistent gains
                  """, FileBuffer.SOFT_CAP_CONCURRENT_STREAM_IN_BUFFER, catalog.getStreams().size());
    }

    return new StagingConsumerFactory().create(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        new RedshiftS3StagingSqlOperations(getNamingResolver(), s3Config.getS3Client(), s3Config, encryptionConfig),
        getNamingResolver(),
        CsvSerializedBuffer.createFunction(null, () -> new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX, numberOfFileBuffers)),
        config,
        catalog,
        isPurgeStagingData(s3Options));
  }

  /**
   * Retrieves user configured file buffer amount so as long it doesn't exceed the maximum number
   * of file buffers and sets the minimum number to the default
   *
   * NOTE: If Out Of Memory Exceptions (OOME) occur, this can be a likely cause as this hard limit
   * has not been thoroughly load tested across all instance sizes
   *
   * @param config user configurations
   * @return number of file buffers if configured otherwise default
   */
  @VisibleForTesting
  public int getNumberOfFileBuffers(final JsonNode config) {
    int numOfFileBuffers = FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER;
    if (config.has(FileBuffer.FILE_BUFFER_COUNT_KEY)) {
      numOfFileBuffers = Math.min(config.get(FileBuffer.FILE_BUFFER_COUNT_KEY).asInt(), FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER);
    }
    // Only allows for values 10 <= numOfFileBuffers <= 50
    return Math.max(numOfFileBuffers, FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  private boolean isPurgeStagingData(final JsonNode config) {
    return !config.has("purge_staging_data") || config.get("purge_staging_data").asBoolean();
  }

}
