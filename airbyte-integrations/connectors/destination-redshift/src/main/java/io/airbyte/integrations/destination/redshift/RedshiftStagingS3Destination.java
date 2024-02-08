/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;
import static io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.getS3DestinationConfig;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.SSL_JDBC_PARAMETERS;
import static io.airbyte.integrations.destination.redshift.RedshiftInsertDestination.getJdbcConfig;
import static io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.UPLOADING_METHOD;
import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.findS3Options;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator;
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryption;
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryption.KeyType;
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig;
import io.airbyte.cdk.integrations.destination.s3.NoEncryption;
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations;
import io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.NoopV2TableMigrator;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.redshift.operations.RedshiftS3StagingSqlOperations;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator;
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStagingS3Destination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStagingS3Destination.class);

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new RedshiftStagingS3Destination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public RedshiftStagingS3Destination() {
    super(RedshiftInsertDestination.DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations());
  }

  private boolean isEphemeralKeysAndPurgingStagingData(final JsonNode config, final EncryptionConfig encryptionConfig) {
    return !isPurgeStagingData(config) && encryptionConfig instanceof final AesCbcEnvelopeEncryption c && c.keyType() == KeyType.EPHEMERAL;
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
      attemptTableOperations(outputSchema, database, nameTransformer, redshiftS3StagingSqlOperations, false);
      RedshiftUtil.checkSvvTableAccess(database);
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
        getDefaultConnectionProperties(config),
        Duration.ofMinutes(2));
  }

  @Override
  protected NamingConventionTransformer getNamingResolver() {
    return new RedshiftSQLNameTransformer();
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    // TODO: Pull common code from RedshiftInsertDestination and RedshiftStagingS3Destination into a
    // base class.
    // The following properties can be overriden through jdbcUrlParameters in the config.
    final Map<String, String> connectionOptions = new HashMap<>();
    // Redshift properties
    // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-configuration-options.html#jdbc20-connecttimeout-option
    // connectTimeout is different from Hikari pool's connectionTimout, driver defaults to 10seconds so
    // increase it to match hikari's default
    connectionOptions.put("connectTimeout", "120");
    // HikariPool properties
    // https://github.com/brettwooldridge/HikariCP?tab=readme-ov-file#frequently-used
    // connectionTimeout is set explicitly to 2 minutes when creating data source.
    // Do aggressive keepAlive with minimum allowed value, this only applies to connection sitting idle
    // in the pool.
    connectionOptions.put("keepaliveTime", Long.toString(Duration.ofSeconds(30).toMillis()));
    connectionOptions.putAll(SSL_JDBC_PARAMETERS);
    return connectionOptions;
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new RedshiftSqlGenerator(getNamingResolver());
  }

  @Override
  protected JdbcDestinationHandler getDestinationHandler(final String databaseName, final JdbcDatabase database) {
    return new RedshiftDestinationHandler(databaseName, database);
  }

  @Override
  @Deprecated
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
    final EncryptionConfig encryptionConfig =
        config.has(UPLOADING_METHOD) ? EncryptionConfig.fromJson(config.get(UPLOADING_METHOD).get(JdbcUtils.ENCRYPTION_KEY)) : new NoEncryption();
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

    final String defaultNamespace = config.get("schema").asText();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().setNamespace(defaultNamespace);
      }
    }
    final RedshiftSqlGenerator sqlGenerator = new RedshiftSqlGenerator(getNamingResolver());
    final ParsedCatalog parsedCatalog;
    final TyperDeduper typerDeduper;
    final JdbcDatabase database = getDatabase(getDataSource(config));
    final String databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final RedshiftDestinationHandler redshiftDestinationHandler = new RedshiftDestinationHandler(databaseName, database);
    final CatalogParser catalogParser;
    if (TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent()) {
      catalogParser = new CatalogParser(sqlGenerator, TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get());
    } else {
      catalogParser = new CatalogParser(sqlGenerator);
    }
    parsedCatalog = catalogParser.parseCatalog(catalog);
    final JdbcV1V2Migrator migrator = new JdbcV1V2Migrator(getNamingResolver(), database, databaseName);
    final NoopV2TableMigrator v2TableMigrator = new NoopV2TableMigrator();
    final boolean disableTypeDedupe = config.has(DISABLE_TYPE_DEDUPE) && config.get(DISABLE_TYPE_DEDUPE).asBoolean(false);
    final int defaultThreadCount = 8;
    if (disableTypeDedupe) {
      typerDeduper = new NoOpTyperDeduperWithV1V2Migrations<>(sqlGenerator, redshiftDestinationHandler, parsedCatalog, migrator, v2TableMigrator,
          defaultThreadCount);
    } else {
      typerDeduper =
          new DefaultTyperDeduper<>(sqlGenerator, redshiftDestinationHandler, parsedCatalog, migrator, v2TableMigrator, defaultThreadCount);
    }
    return StagingConsumerFactory.builder(
        outputRecordCollector,
        database,
        new RedshiftS3StagingSqlOperations(getNamingResolver(), s3Config.getS3Client(), s3Config, encryptionConfig),
        getNamingResolver(),
        config,
        catalog,
        isPurgeStagingData(s3Options),
        new TypeAndDedupeOperationValve(),
        typerDeduper,
        parsedCatalog,
        defaultNamespace,
        true).build().createAsync();
  }

  /**
   * Retrieves user configured file buffer amount so as long it doesn't exceed the maximum number of
   * file buffers and sets the minimum number to the default
   *
   * NOTE: If Out Of Memory Exceptions (OOME) occur, this can be a likely cause as this hard limit has
   * not been thoroughly load tested across all instance sizes
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
