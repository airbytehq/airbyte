/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.codepoetics.protonpack.StreamUtils;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsAvroBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsCsvBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.gcs.GcsDestination;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsStorageOperations;
import io.airbyte.integrations.destination.gcs.util.GcsUtils;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;
import org.apache.avro.Schema;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestination.class);
  private static final List<String> REQUIRED_PERMISSIONS = List.of(
      "storage.multipartUploads.abort",
      "storage.multipartUploads.create",
      "storage.objects.create",
      "storage.objects.delete",
      "storage.objects.get",
      "storage.objects.list");
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

  protected BigQuery getBigQuery(final JsonNode config) {
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
   * @param outputRecordCollector
   * @return
   * @throws IOException
   */
  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException {
    final UploadingMethod uploadingMethod = BigQueryUtils.getLoadingMethod(config);
    if (uploadingMethod == UploadingMethod.STANDARD) {
      LOGGER.warn("The \"standard\" upload mode is not performant, and is not recommended for production. " +
          "Please use the GCS upload mode if you are syncing a large amount of data.");
      return getStandardRecordConsumer(config, catalog, outputRecordCollector);
    } else {
      return getGcsRecordConsumer(config, catalog, outputRecordCollector);
    }
  }

  protected Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> getUploaderMap(final JsonNode config,
                                                                                            final ConfiguredAirbyteCatalog catalog)
      throws IOException {
    final BigQuery bigquery = getBigQuery(config);

    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      if (StringUtils.isEmpty(stream.getNamespace())) {
        stream.setNamespace(BigQueryUtils.getDatasetId(config));
      }
      final String streamName = stream.getName();
      final UploaderConfig uploaderConfig = UploaderConfig
          .builder()
          .bigQuery(bigquery)
          .configStream(configStream)
          .config(config)
          .formatterMap(getFormatterMap(stream.getJsonSchema()))
          .tmpTableName(namingResolver.getTmpTableName(streamName))
          .targetTableName(getTargetTableName(streamName))
          .isDefaultAirbyteTmpSchema(isDefaultAirbyteTmpTableSchema())
          .build();

      putStreamIntoUploaderMap(stream, uploaderConfig, uploaderMap);
    }
    return uploaderMap;
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
    return Map.of(UploaderType.STANDARD, new DefaultBigQueryRecordFormatter(jsonSchema, namingResolver),
        UploaderType.CSV, new GcsCsvBigQueryRecordFormatter(jsonSchema, namingResolver),
        UploaderType.AVRO, new GcsAvroBigQueryRecordFormatter(jsonSchema, namingResolver));
  }

  protected String getTargetTableName(final String streamName) {
    return namingResolver.getRawTableName(streamName);
  }

  private AirbyteMessageConsumer getStandardRecordConsumer(final JsonNode config,
                                                           final ConfiguredAirbyteCatalog catalog,
                                                           final Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> writeConfigs = getUploaderMap(config, catalog);
    return new BigQueryRecordConsumer(writeConfigs, outputRecordCollector, BigQueryUtils.getDatasetId(config));
  }

  public AirbyteMessageConsumer getGcsRecordConsumer(final JsonNode config,
                                                     final ConfiguredAirbyteCatalog catalog,
                                                     final Consumer<AirbyteMessage> outputRecordCollector) {

    final StandardNameTransformer gcsNameTransformer = new GcsNameTransformer();
    final BigQuery bigQuery = getBigQuery(config);
    final GcsDestinationConfig gcsConfig = BigQueryUtils.getGcsAvroDestinationConfig(config);
    final UUID stagingId = UUID.randomUUID();
    final DateTime syncDatetime = DateTime.now(DateTimeZone.UTC);
    final boolean keepStagingFiles = BigQueryUtils.isKeepFilesInGcs(config);
    final GcsStorageOperations gcsOperations = new GcsStorageOperations(gcsNameTransformer, gcsConfig.getS3Client(), gcsConfig);
    final BigQueryStagingOperations bigQueryGcsOperations = new BigQueryGcsOperations(
        bigQuery,
        gcsNameTransformer,
        gcsConfig,
        gcsOperations,
        stagingId,
        syncDatetime,
        keepStagingFiles);
    final S3AvroFormatConfig avroFormatConfig = (S3AvroFormatConfig) gcsConfig.getFormatConfig();
    final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator = getRecordFormatterCreator(namingResolver);
    final int numberOfFileBuffers = getNumberOfFileBuffers(config);

    if (numberOfFileBuffers > FileBuffer.SOFT_CAP_CONCURRENT_STREAM_IN_BUFFER) {
      LOGGER.warn("""
                  Increasing the number of file buffers past {} can lead to increased performance but
                  leads to increased memory usage. If the number of file buffers exceeds the number
                  of streams {} this will create more buffers than necessary, leading to nonexistent gains
                  """, FileBuffer.SOFT_CAP_CONCURRENT_STREAM_IN_BUFFER, catalog.getStreams().size());
    }

    final BufferCreateFunction onCreateBuffer =
        BigQueryAvroSerializedBuffer.createBufferFunction(
            avroFormatConfig,
            recordFormatterCreator,
            getAvroSchemaCreator(),
            () -> new FileBuffer(S3AvroFormatConfig.DEFAULT_SUFFIX, numberOfFileBuffers));

    LOGGER.info("Creating BigQuery staging message consumer with staging ID {} at {}", stagingId, syncDatetime);
    return new BigQueryStagingConsumerFactory().create(
        config,
        catalog,
        outputRecordCollector,
        bigQueryGcsOperations,
        onCreateBuffer,
        recordFormatterCreator,
        namingResolver::getTmpTableName,
        getTargetTableNameTransformer(namingResolver));
  }

  protected BiFunction<BigQueryRecordFormatter, AirbyteStreamNameNamespacePair, Schema> getAvroSchemaCreator() {
    return (formatter, pair) -> GcsUtils.getDefaultAvroSchema(pair.getName(), pair.getNamespace(), true);
  }

  protected Function<JsonNode, BigQueryRecordFormatter> getRecordFormatterCreator(final BigQuerySQLNameTransformer namingResolver) {
    return streamSchema -> new GcsAvroBigQueryRecordFormatter(streamSchema, namingResolver);
  }

  protected Function<String, String> getTargetTableNameTransformer(final BigQuerySQLNameTransformer namingResolver) {
    return namingResolver::getRawTableName;
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

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    new IntegrationRunner(destination).run(args);
  }

}
