/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.codepoetics.protonpack.StreamUtils;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.base.Charsets;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsCsvBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV1V2Migrator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV2TableMigrator;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.gcs.GcsDestination;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsStorageOperations;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDestination extends BaseConnector implements Destination {

  private static final String RAW_DATA_DATASET = "raw_data_dataset";

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestination.class);
  private static final List<String> REQUIRED_PERMISSIONS = List.of(
      "storage.multipartUploads.abort",
      "storage.multipartUploads.create",
      "storage.objects.create",
      "storage.objects.delete",
      "storage.objects.get",
      "storage.objects.list");
  private static final ConcurrentMap<AirbyteStreamNameNamespacePair, String> randomSuffixMap = new ConcurrentHashMap<>();
  protected final BigQuerySQLNameTransformer namingResolver;

  public BigQueryDestination() {
    namingResolver = new BigQuerySQLNameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final String datasetId = BigQueryUtils.getDatasetId(config);
      final String datasetLocation = BigQueryUtils.getDatasetLocation(config);
      final BigQuery bigquery = getBigQuery(config);
      final UploadingMethod uploadingMethod = BigQueryUtils.getLoadingMethod(config);

      BigQueryUtils.checkHasCreateAndDeleteDatasetRole(bigquery, datasetId, datasetLocation);

      final Dataset dataset = BigQueryUtils.getOrCreateDataset(bigquery, datasetId, datasetLocation);
      if (!dataset.getLocation().equals(datasetLocation)) {
        throw new ConfigErrorException("Actual dataset location doesn't match to location from config");
      }
      final QueryJobConfiguration queryConfig = QueryJobConfiguration
          .newBuilder(String.format("SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES` LIMIT 1;", datasetId))
          .setUseLegacySql(false)
          .build();

      if (UploadingMethod.GCS.equals(uploadingMethod)) {
        final AirbyteConnectionStatus status = checkGcsPermission(config);
        if (!status.getStatus().equals(Status.SUCCEEDED)) {
          return status;
        }
      }

      final ImmutablePair<Job, String> result = BigQueryUtils.executeQuery(bigquery, queryConfig);
      if (result.getLeft() != null) {
        return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
      } else {
        throw new ConfigErrorException(result.getRight());
      }
    } catch (final Exception e) {
      LOGGER.error("Check failed.", e);
      throw new ConfigErrorException(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  /**
   * This method does two checks: 1) permissions related to the bucket, and 2) the ability to create
   * and delete an actual file. The latter is important because even if the service account may have
   * the proper permissions, the HMAC keys can only be verified by running the actual GCS check.
   */
  private AirbyteConnectionStatus checkGcsPermission(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    final String bucketName = loadingMethod.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
    final List<String> missingPermissions = new ArrayList<>();

    try {
      final GoogleCredentials credentials = getServiceAccountCredentials(config);
      final Storage storage = StorageOptions.newBuilder()
          .setProjectId(config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText())
          .setCredentials(credentials)
          .setHeaderProvider(BigQueryUtils.getHeaderProvider())
          .build().getService();
      final List<Boolean> permissionsCheckStatusList = storage.testIamPermissions(bucketName, REQUIRED_PERMISSIONS);

      missingPermissions.addAll(StreamUtils
          .zipWithIndex(permissionsCheckStatusList.stream())
          .filter(i -> !i.getValue())
          .map(i -> REQUIRED_PERMISSIONS.get(Math.toIntExact(i.getIndex())))
          .toList());

      final GcsDestination gcsDestination = new GcsDestination();
      final JsonNode gcsJsonNodeConfig = BigQueryUtils.getGcsJsonNodeConfig(config);
      return gcsDestination.check(gcsJsonNodeConfig);
    } catch (final Exception e) {
      final StringBuilder message = new StringBuilder("Cannot access the GCS bucket.");
      if (!missingPermissions.isEmpty()) {
        message.append(" The following permissions are missing on the service account: ")
            .append(String.join(", ", missingPermissions))
            .append(".");
      }
      message.append(" Please make sure the service account can access the bucket path, and the HMAC keys are correct.");

      LOGGER.error(message.toString(), e);
      throw new ConfigErrorException("Could not access the GCS bucket with the provided configuration.\n", e);
    }
  }

  public static BigQuery getBigQuery(final JsonNode config) {
    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    try {
      final BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
      final GoogleCredentials credentials = getServiceAccountCredentials(config);
      return bigQueryBuilder
          .setProjectId(projectId)
          .setCredentials(credentials)
          .setHeaderProvider(BigQueryUtils.getHeaderProvider())
          .build()
          .getService();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static GoogleCredentials getServiceAccountCredentials(final JsonNode config) throws IOException {
    if (!BigQueryUtils.isUsingJsonCredentials(config)) {
      LOGGER.info("No service account key json is provided. It is required if you are using Airbyte cloud.");
      LOGGER.info("Using the default service account credential from environment.");
      return GoogleCredentials.getApplicationDefault();
    }

    // The JSON credential can either be a raw JSON object, or a serialized JSON object.
    final String credentialsString = config.get(BigQueryConsts.CONFIG_CREDS).isObject()
        ? Jsons.serialize(config.get(BigQueryConsts.CONFIG_CREDS))
        : config.get(BigQueryConsts.CONFIG_CREDS).asText();
    return GoogleCredentials.fromStream(
        new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
  }

  /**
   * Returns a {@link AirbyteMessageConsumer} based on whether the uploading mode is STANDARD INSERTS
   * or using STAGING
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   */
  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    throw new UnsupportedOperationException("Should use getSerializedMessageConsumer");
  }

  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    final UploadingMethod uploadingMethod = BigQueryUtils.getLoadingMethod(config);
    final String defaultNamespace = BigQueryUtils.getDatasetId(config);
    setDefaultStreamNamespace(catalog, defaultNamespace);
    final boolean disableTypeDedupe = BigQueryUtils.getDisableTypeDedupFlag(config);
    final String datasetLocation = BigQueryUtils.getDatasetLocation(config);
    final BigQuerySqlGenerator sqlGenerator = new BigQuerySqlGenerator(config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText(), datasetLocation);
    final ParsedCatalog parsedCatalog = parseCatalog(config, catalog, datasetLocation);
    final BigQuery bigquery = getBigQuery(config);
    final TyperDeduper typerDeduper = buildTyperDeduper(sqlGenerator, parsedCatalog, bigquery, datasetLocation, disableTypeDedupe);

    AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(config);
    final JsonNode serviceAccountKey = config.get(BigQueryConsts.CONFIG_CREDS);
    if (serviceAccountKey.isTextual()) {
      // There are cases where we fail to deserialize the service account key. In these cases, we
      // shouldn't do anything.
      // Google's creds library is more lenient with JSON-parsing than Jackson, and I'd rather just let it
      // go.
      Jsons.tryDeserialize(serviceAccountKey.asText())
          .ifPresent(AirbyteExceptionHandler::addAllStringsInConfigForDeinterpolation);
    } else {
      AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(serviceAccountKey);
    }

    if (uploadingMethod == UploadingMethod.STANDARD) {
      LOGGER.warn("The \"standard\" upload mode is not performant, and is not recommended for production. " +
          "Please use the GCS upload mode if you are syncing a large amount of data.");
      return getStandardRecordConsumer(bigquery, config, catalog, parsedCatalog, outputRecordCollector, typerDeduper);
    }

    final StandardNameTransformer gcsNameTransformer = new GcsNameTransformer();
    final GcsDestinationConfig gcsConfig = BigQueryUtils.getGcsCsvDestinationConfig(config);
    final UUID stagingId = UUID.randomUUID();
    final DateTime syncDatetime = DateTime.now(DateTimeZone.UTC);
    final boolean keepStagingFiles = BigQueryUtils.isKeepFilesInGcs(config);
    final GcsStorageOperations gcsOperations = new GcsStorageOperations(gcsNameTransformer, gcsConfig.getS3Client(), gcsConfig);
    final BigQueryStagingOperations bigQueryGcsOperations = new BigQueryGcsOperations(
        bigquery,
        gcsNameTransformer,
        gcsConfig,
        gcsOperations,
        stagingId,
        syncDatetime,
        keepStagingFiles);

    return new BigQueryStagingConsumerFactory().createAsync(
        config,
        catalog,
        outputRecordCollector,
        bigQueryGcsOperations,
        getCsvRecordFormatterCreator(namingResolver),
        namingResolver::getTmpTableName,
        typerDeduper,
        parsedCatalog,
        BigQueryUtils.getDatasetId(config));
  }

  protected Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> getUploaderMap(
                                                                                                                final BigQuery bigquery,
                                                                                                                final JsonNode config,
                                                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                                                final ParsedCatalog parsedCatalog)
      throws IOException {
    return () -> {
      final ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new ConcurrentHashMap<>();
      for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
        final AirbyteStream stream = configStream.getStream();
        final StreamConfig parsedStream;

        randomSuffixMap.putIfAbsent(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream), RandomStringUtils.randomAlphabetic(3).toLowerCase());

        final String randomSuffix = randomSuffixMap.get(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream));
        final String streamName = stream.getName();
        final String targetTableName;

        parsedStream = parsedCatalog.getStream(stream.getNamespace(), stream.getName());
        targetTableName = parsedStream.id().rawName();

        final UploaderConfig uploaderConfig = UploaderConfig
            .builder()
            .bigQuery(bigquery)
            .configStream(configStream)
            .parsedStream(parsedStream)
            .config(config)
            .formatterMap(getFormatterMap(stream.getJsonSchema()))
            .tmpTableName(namingResolver.getTmpTableName(streamName, randomSuffix))
            .targetTableName(targetTableName)
            // This refers to whether this is BQ denormalized or not
            .isDefaultAirbyteTmpSchema(isDefaultAirbyteTmpTableSchema())
            .build();

        try {
          putStreamIntoUploaderMap(stream, uploaderConfig, uploaderMap);
        } catch (final IOException e) {
          throw new RuntimeException(e);
        }
      }
      return uploaderMap;
    };
  }

  protected void putStreamIntoUploaderMap(final AirbyteStream stream,
                                          final UploaderConfig uploaderConfig,
                                          final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap)
      throws IOException {
    uploaderMap.put(
        AirbyteStreamNameNamespacePair.fromAirbyteStream(stream),
        BigQueryUploaderFactory.getUploader(uploaderConfig));
  }

  /**
   * BigQuery might have different structure of the Temporary table. If this method returns TRUE,
   * temporary table will have only three common Airbyte attributes. In case of FALSE, temporary table
   * structure will be in line with Airbyte message JsonSchema.
   *
   * @return use default AirbyteSchema or build using JsonSchema
   */
  protected boolean isDefaultAirbyteTmpTableSchema() {
    return true;
  }

  protected Map<UploaderType, BigQueryRecordFormatter> getFormatterMap(final JsonNode jsonSchema) {
    return Map.of(
        UploaderType.STANDARD, new DefaultBigQueryRecordFormatter(jsonSchema, namingResolver),
        UploaderType.CSV, new GcsCsvBigQueryRecordFormatter(jsonSchema, namingResolver));
  }

  private SerializedAirbyteMessageConsumer getStandardRecordConsumer(final BigQuery bigquery,
                                                                     final JsonNode config,
                                                                     final ConfiguredAirbyteCatalog catalog,
                                                                     final ParsedCatalog parsedCatalog,
                                                                     final Consumer<AirbyteMessage> outputRecordCollector,
                                                                     final TyperDeduper typerDeduper)
      throws Exception {
    typerDeduper.prepareTables();
    final Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> writeConfigs = getUploaderMap(
        bigquery,
        config,
        catalog,
        parsedCatalog);

    final String bqNamespace = BigQueryUtils.getDatasetId(config);

    return new BigQueryRecordStandardConsumer(
        outputRecordCollector,
        () -> {
          // Set up our raw tables
          writeConfigs.get().forEach((streamId, uploader) -> {
            final StreamConfig stream = parsedCatalog.getStream(streamId);
            if (stream.destinationSyncMode() == DestinationSyncMode.OVERWRITE) {
              // For streams in overwrite mode, truncate the raw table.
              // non-1s1t syncs actually overwrite the raw table at the end of the sync, so we only do this in
              // 1s1t mode.
              final TableId rawTableId = TableId.of(stream.id().rawNamespace(), stream.id().rawName());
              LOGGER.info("Deleting Raw table {}", rawTableId);
              if (!bigquery.delete(rawTableId)) {
                LOGGER.info("Raw table {} not found, continuing with creation", rawTableId);
              }
              LOGGER.info("Creating table {}", rawTableId);
              BigQueryUtils.createPartitionedTableIfNotExists(bigquery, rawTableId, DefaultBigQueryRecordFormatter.SCHEMA_V2);
            } else {
              uploader.createRawTable();
            }
          });
        },
        (hasFailed) -> {
          try {
            Thread.sleep(30 * 1000);
            typerDeduper.typeAndDedupe();
            typerDeduper.commitFinalTables();
            typerDeduper.cleanup();
          } catch (final Exception e) {
            throw new RuntimeException(e);
          }
        },
        bigquery,
        catalog,
        bqNamespace,
        writeConfigs);
  }

  protected Function<JsonNode, BigQueryRecordFormatter> getCsvRecordFormatterCreator(final BigQuerySQLNameTransformer namingResolver) {
    return streamSchema -> new GcsCsvBigQueryRecordFormatter(streamSchema, namingResolver);
  }

  private void setDefaultStreamNamespace(final ConfiguredAirbyteCatalog catalog, final String namespace) {
    // Set the default namespace on streams with null namespace. This means we don't need to repeat this
    // logic in the rest of the connector.
    // (record messages still need to handle null namespaces though, which currently happens in e.g.
    // AsyncStreamConsumer#accept)
    // This probably should be shared logic amongst destinations eventually.
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().withNamespace(namespace);
      }
    }
  }

  private ParsedCatalog parseCatalog(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final String datasetLocation) {
    final BigQuerySqlGenerator sqlGenerator = new BigQuerySqlGenerator(config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText(), datasetLocation);
    final CatalogParser catalogParser = TypingAndDedupingFlag.getRawNamespaceOverride(RAW_DATA_DATASET).isPresent()
        ? new CatalogParser(sqlGenerator, TypingAndDedupingFlag.getRawNamespaceOverride(RAW_DATA_DATASET).get())
        : new CatalogParser(sqlGenerator);

    return catalogParser.parseCatalog(catalog);
  }

  private TyperDeduper buildTyperDeduper(final BigQuerySqlGenerator sqlGenerator,
                                         final ParsedCatalog parsedCatalog,
                                         final BigQuery bigquery,
                                         final String datasetLocation,
                                         final boolean disableTypeDedupe) {
    final BigQueryV1V2Migrator migrator = new BigQueryV1V2Migrator(bigquery, namingResolver);
    final BigQueryV2TableMigrator v2RawTableMigrator = new BigQueryV2TableMigrator(bigquery);
    final BigQueryDestinationHandler destinationHandler = new BigQueryDestinationHandler(bigquery, datasetLocation);

    if (disableTypeDedupe) {
      return new NoOpTyperDeduperWithV1V2Migrations<>(
          sqlGenerator, destinationHandler, parsedCatalog, migrator, v2RawTableMigrator, 8);
    }

    return new DefaultTyperDeduper<>(
        sqlGenerator,
        destinationHandler,
        parsedCatalog,
        migrator,
        v2RawTableMigrator,
        8);

  }

  public static void main(final String[] args) throws Exception {
    AirbyteExceptionHandler.addThrowableForDeinterpolation(BigQueryException.class);
    final Destination destination = new BigQueryDestination();
    new IntegrationRunner(destination).run(args);
  }

}
