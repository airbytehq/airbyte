/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.common.base.Charsets;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
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
import io.airbyte.integrations.destination.bigquery.uploader.GcsCsvBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.gcs.GcsDestination;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.record_buffer.BufferingStrategy;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.s3.csv.CsvSheetGenerator;
import io.airbyte.integrations.destination.s3.csv.NoFlatteningSheetGenerator;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestination.class);

  private final BigQuerySQLNameTransformer namingResolver;

  public BigQueryDestination() {
    namingResolver = new BigQuerySQLNameTransformer();
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    new IntegrationRunner(destination).run(args);
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

      // GCS upload time re-uses destination-GCS for check and other uploading (CSV format writer)
      if (UploadingMethod.GCS.equals(uploadingMethod)) {
        final GcsDestination gcsDestination = new GcsDestination();
        final JsonNode gcsJsonNodeConfig = BigQueryUtils.getGcsJsonNodeConfig(config);
        final AirbyteConnectionStatus airbyteConnectionStatus = gcsDestination.check(gcsJsonNodeConfig);
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
        final String credentialsString = config.get(BigQueryConsts.CONFIG_CREDS).isObject()
            ? Jsons.serialize(config.get(BigQueryConsts.CONFIG_CREDS))
            : config.get(BigQueryConsts.CONFIG_CREDS).asText();
        credentials = ServiceAccountCredentials
            .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
      }
      return bigQueryBuilder
          .setProjectId(projectId)
          .setCredentials(credentials != null ? credentials : ServiceAccountCredentials.getApplicationDefault())
          .build()
          .getService();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return new BigQueryRecordConsumer(outputRecordCollector, getBufferingStrategy(catalog), catalog);
  }

  private BufferingStrategy getBufferingStrategy(final ConfiguredAirbyteCatalog catalog) {
    return new SerializedBufferingStrategy(
        createBufferFunction(),
        catalog,
        flushBufferFunction());
  }

  final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> createBufferFunction() {
    final CsvSheetGenerator csvSheetGenerator = new NoFlatteningSheetGenerator();
    return (stream, catalog) -> new CsvSerializedBuffer(new FileBuffer(), csvSheetGenerator)
        .withCsvFormat(GcsCsvBigQueryUploader.getCsvFormat(csvSheetGenerator));
  }

  private CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> flushBufferFunction() {
    return (stream, buffer) -> {
      LOGGER.info("Flushing buffer for stream {} ({}) to staging", stream.getName(), FileUtils.byteCountToDisplaySize(buffer.getByteCount()));
      if (!pairToWriteConfig.containsKey(stream)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(stream);
      final String schemaName = writeConfig.getOutputSchemaName();
      final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
      final String stagingPath =
          stagingOperations.getStagingPath(RANDOM_CONNECTION_ID, schemaName, writeConfig.getStreamName(), writeConfig.getWriteDatetime());
      try (buffer) {
        buffer.flush();
        writeConfig.addStagedFile(stagingOperations.uploadRecordsToStage(database, buffer, schemaName, stageName, stagingPath));
      } catch (final Exception e) {
        LOGGER.error("Failed to flush and upload buffer to stage:", e);
        throw new RuntimeException("Failed to upload buffer to stage", e);
      }
    };
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
   * BigQuery might have different structure of the Temporary table. If this method returns TRUE, temporary table will have only three common Airbyte
   * attributes. In case of FALSE, temporary table structure will be in line with Airbyte message JsonSchema.
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

}
