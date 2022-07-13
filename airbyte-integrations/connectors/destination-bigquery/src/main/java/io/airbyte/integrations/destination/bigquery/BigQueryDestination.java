/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.codepoetics.protonpack.StreamUtils;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.base.Charsets;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
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
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
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

      BigQueryUtils.createDataset(bigquery, datasetId, datasetLocation);
      final QueryJobConfiguration queryConfig = QueryJobConfiguration
          .newBuilder(String.format("SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES` LIMIT 1;", datasetId))
          .setUseLegacySql(false)
          .build();

      if (UploadingMethod.GCS.equals(uploadingMethod)) {
        final AirbyteConnectionStatus airbyteConnectionStatus = checkGcsPermission(config);
        if (Status.FAILED == airbyteConnectionStatus.getStatus()) {
          return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(airbyteConnectionStatus.getMessage());
        }
      }

      final ImmutablePair<Job, String> result = BigQueryUtils.executeQuery(bigquery, queryConfig);
      if (result.getLeft() != null) {
        return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
      } else {
        return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(result.getRight());
      }
    } catch (final Exception e) {
      LOGGER.error("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  /**
   * This method does two checks: 1) permissions related to the bucket, and 2) the ability to create
   * and delete an actual file. The latter is important because even if the service account may have
   * the proper permissions, the HMAC keys can only be verified by running the actual GCS check.
   */
  public AirbyteConnectionStatus checkGcsPermission(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    final String bucketName = loadingMethod.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
    final List<String> missingPermissions = new ArrayList<>();

    try {
      final GoogleCredentials credentials = getServiceAccountCredentials(config);
      final Storage storage = StorageOptions.newBuilder()
          .setProjectId(config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText())
          .setCredentials(credentials)
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

      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could access the GCS bucket with the provided configuration.\n" + e
              .getMessage());
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
          .build()
          .getService();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static GoogleCredentials getServiceAccountCredentials(final JsonNode config) throws IOException {
    if (!BigQueryUtils.isUsingJsonCredentials(config)) {
      LOGGER.info("No service account key json is provided. It is required if you are using Airbyte cloud.");
      LOGGER.info("Using the default service account credential from environment.");
      return ServiceAccountCredentials.getApplicationDefault();
    }

    // The JSON credential can either be a raw JSON object, or a serialized JSON object.
    final String credentialsString = config.get(BigQueryConsts.CONFIG_CREDS).isObject()
        ? Jsons.serialize(config.get(BigQueryConsts.CONFIG_CREDS))
        : config.get(BigQueryConsts.CONFIG_CREDS).asText();
    return ServiceAccountCredentials.fromStream(
        new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
  }

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

      uploaderMap.put(
          AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
          BigQueryUploaderFactory.getUploader(uploaderConfig));
    }
    return uploaderMap;
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
    return new BigQueryRecordConsumer(writeConfigs, outputRecordCollector);
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
    final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer =
        BigQueryAvroSerializedBuffer.createFunction(
            avroFormatConfig,
            recordFormatterCreator,
            getAvroSchemaCreator(),
            () -> new FileBuffer(S3AvroFormatConfig.DEFAULT_SUFFIX));

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

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    new IntegrationRunner(destination).run(args);
  }

}
