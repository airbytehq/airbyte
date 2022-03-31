/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static java.util.Objects.isNull;

import com.codepoetics.protonpack.StreamUtils;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsAvroBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsCsvBigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
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
  private final BigQuerySQLNameTransformer namingResolver;

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

      BigQueryUtils.createSchemaTable(bigquery, datasetId, datasetLocation);
      final QueryJobConfiguration queryConfig = QueryJobConfiguration
          .newBuilder(String.format("SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES` LIMIT 1;", datasetId))
          .setUseLegacySql(false)
          .build();

      if (UploadingMethod.GCS.equals(uploadingMethod)) {
        // TODO: use GcsDestination::check instead of writing our own custom logic to check perms
        // this is not currently possible because using the Storage class to check perms requires
        // a service account key, and the GCS destination does not accept a Service Account Key,
        // only an HMAC key
        final AirbyteConnectionStatus airbyteConnectionStatus = checkStorageIamPermissions(config);
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
      LOGGER.info("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  public AirbyteConnectionStatus checkStorageIamPermissions(JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    final String bucketName = loadingMethod.get(BigQueryConsts.GCS_BUCKET_NAME).asText();

    try {
      ServiceAccountCredentials credentials = getServiceAccountCredentials(config);

      Storage storage = StorageOptions.newBuilder()
          .setProjectId(config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText())
          .setCredentials(!isNull(credentials) ? credentials : ServiceAccountCredentials.getApplicationDefault())
          .build().getService();
      List<Boolean> permissionsCheckStatusList = storage.testIamPermissions(bucketName, REQUIRED_PERMISSIONS);

      List<String> missingPermissions = StreamUtils
          .zipWithIndex(permissionsCheckStatusList.stream())
          .filter(i -> !i.getValue())
          .map(i -> REQUIRED_PERMISSIONS.get(Math.toIntExact(i.getIndex())))
          .collect(Collectors.toList());

      if (!missingPermissions.isEmpty()) {
        LOGGER.error("Please make sure you account has all of these permissions:{}", REQUIRED_PERMISSIONS);

        return new AirbyteConnectionStatus()
            .withStatus(AirbyteConnectionStatus.Status.FAILED)
            .withMessage("Could not connect to the Gcs bucket with the provided configuration. "
                + "Missing permissions: " + missingPermissions);
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);

    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the Gcs bucket: {}", e.getMessage());

      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the Gcs bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  protected BigQuerySQLNameTransformer getNamingResolver() {
    return namingResolver;
  }

  protected BigQuery getBigQuery(final JsonNode config) {
    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    try {
      final BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
      ServiceAccountCredentials credentials = null;
      if (BigQueryUtils.isUsingJsonCredentials(config)) {
        // handle the credentials json being passed as a json object or a json object already serialized as
        // a string.
        credentials = getServiceAccountCredentials(config);
      }
      return bigQueryBuilder
          .setProjectId(projectId)
          .setCredentials(!isNull(credentials) ? credentials : ServiceAccountCredentials.getApplicationDefault())
          .build()
          .getService();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private ServiceAccountCredentials getServiceAccountCredentials(JsonNode config) throws IOException {
    ServiceAccountCredentials credentials;
    final String credentialsString =
        config.get(BigQueryConsts.CONFIG_CREDS).isObject() ? Jsons.serialize(config.get(BigQueryConsts.CONFIG_CREDS))
            : config.get(BigQueryConsts.CONFIG_CREDS).asText();
    credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
    return credentials;
  }

  /**
   * Strategy:
   * <p>
   * 1. Create a temporary table for each stream
   * </p>
   * <p>
   * 2. Write records to each stream directly (the bigquery client handles managing when to push the
   * records over the network)
   * </p>
   * <p>
   * 4. Once all records have been written close the writers, so that any remaining records are
   * flushed.
   * </p>
   * <p>
   * 5. Copy the temp tables to the final table name (overwriting if necessary).
   * </p>
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   * @return consumer that writes singer messages to the database.
   */
  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException {
    return getRecordConsumer(getUploaderMap(config, catalog), outputRecordCollector);
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
    return Map.of(UploaderType.STANDARD, new DefaultBigQueryRecordFormatter(jsonSchema, getNamingResolver()),
        UploaderType.CSV, new GcsCsvBigQueryRecordFormatter(jsonSchema, getNamingResolver()),
        UploaderType.AVRO, new GcsAvroBigQueryRecordFormatter(jsonSchema, getNamingResolver()));
  }

  protected String getTargetTableName(final String streamName) {
    return namingResolver.getRawTableName(streamName);
  }

  protected AirbyteMessageConsumer getRecordConsumer(final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> writeConfigs,
                                                     final Consumer<AirbyteMessage> outputRecordCollector) {
    return new BigQueryRecordConsumer(writeConfigs, outputRecordCollector);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    new IntegrationRunner(destination).run(args);
  }

}
