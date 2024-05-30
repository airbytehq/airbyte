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
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator;
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
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.NoopV2TableMigrator;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.destination.redshift.operations.RedshiftS3StagingSqlOperations;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftRawTableAirbyteMetaMigration;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftState;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSuperLimitationTransformer;
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStagingS3Destination extends AbstractJdbcDestination<RedshiftState> implements Destination {

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
        config.has(UPLOADING_METHOD) ? EncryptionConfig.fromJson(config.get(UPLOADING_METHOD).get(JdbcUtils.ENCRYPTION_KEY))
            : new NoEncryption();
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
  protected JdbcSqlGenerator getSqlGenerator(final JsonNode config) {
    return new RedshiftSqlGenerator(getNamingResolver(), config);
  }

  @Override
  protected JdbcDestinationHandler<RedshiftState> getDestinationHandler(final String databaseName,
                                                                        final JdbcDatabase database,
                                                                        String rawTableSchema) {
    return new RedshiftDestinationHandler(databaseName, database, rawTableSchema);
  }

  @Override
  protected List<Migration<RedshiftState>> getMigrations(JdbcDatabase database,
                                                         String databaseName,
                                                         SqlGenerator sqlGenerator,
                                                         DestinationHandler<RedshiftState> destinationHandler) {
    return List.of(new RedshiftRawTableAirbyteMetaMigration(database, databaseName));
  }

  @Override
  protected StreamAwareDataTransformer getDataTransformer(ParsedCatalog parsedCatalog, String defaultNamespace) {
    // Redundant override to keep in consistent with InsertDestination. TODO: Unify these 2 classes with
    // composition.
    return new RedshiftSuperLimitationTransformer(parsedCatalog, defaultNamespace);
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
        config.has(UPLOADING_METHOD) ? EncryptionConfig.fromJson(config.get(UPLOADING_METHOD).get(JdbcUtils.ENCRYPTION_KEY))
            : new NoEncryption();
    final JsonNode s3Options = findS3Options(config);
    final S3DestinationConfig s3Config = getS3DestinationConfig(s3Options);

    final String defaultNamespace = config.get("schema").asText();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().setNamespace(defaultNamespace);
      }
    }

    final RedshiftSqlGenerator sqlGenerator = new RedshiftSqlGenerator(getNamingResolver(), config);
    final ParsedCatalog parsedCatalog;
    final TyperDeduper typerDeduper;
    final JdbcDatabase database = getDatabase(getDataSource(config));
    final String databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final CatalogParser catalogParser;
    final String rawNamespace;
    if (TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent()) {
      rawNamespace = TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get();
      catalogParser = new CatalogParser(sqlGenerator, rawNamespace);
    } else {
      rawNamespace = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
      catalogParser = new CatalogParser(sqlGenerator, rawNamespace);
    }
    final RedshiftDestinationHandler redshiftDestinationHandler = new RedshiftDestinationHandler(databaseName, database, rawNamespace);
    parsedCatalog = catalogParser.parseCatalog(catalog);
    final JdbcV1V2Migrator migrator = new JdbcV1V2Migrator(getNamingResolver(), database, databaseName);
    final NoopV2TableMigrator v2TableMigrator = new NoopV2TableMigrator();
    final boolean disableTypeDedupe = config.has(DISABLE_TYPE_DEDUPE) && config.get(DISABLE_TYPE_DEDUPE).asBoolean(false);
    List<Migration<RedshiftState>> redshiftMigrations = getMigrations(database, databaseName, sqlGenerator, redshiftDestinationHandler);
    if (disableTypeDedupe) {
      typerDeduper =
          new NoOpTyperDeduperWithV1V2Migrations<>(sqlGenerator, redshiftDestinationHandler, parsedCatalog,
              migrator, v2TableMigrator, redshiftMigrations);
    } else {
      typerDeduper =
          new DefaultTyperDeduper<>(sqlGenerator, redshiftDestinationHandler, parsedCatalog, migrator, v2TableMigrator, redshiftMigrations);
    }

    return StagingConsumerFactory.builder(
        outputRecordCollector,
        database,
        new RedshiftS3StagingSqlOperations(getNamingResolver(), s3Config.getS3Client(), s3Config, encryptionConfig),
        getNamingResolver(),
        config,
        catalog,
        isPurgeStagingData(s3Options),
        typerDeduper,
        parsedCatalog,
        defaultNamespace,
        JavaBaseConstants.DestinationColumns.V2_WITH_META)
        .setDataTransformer(getDataTransformer(parsedCatalog, defaultNamespace))
        .build()
        .createAsync();
  }

  private boolean isPurgeStagingData(final JsonNode config) {
    return !config.has("purge_staging_data") || config.get("purge_staging_data").asBoolean();
  }

}
