/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static java.util.Objects.isNull;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.WriteChannelConfiguration;
import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.gcs.GcsDestination;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestination.class);

  private static final com.google.cloud.bigquery.Schema SCHEMA = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING));

  private final BigQuerySQLNameTransformer namingResolver;

  public BigQueryDestination() {
    namingResolver = new BigQuerySQLNameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final String datasetId = config.get(BigQueryConsts.CONFIG_DATASET_ID).asText();
      final String datasetLocation = BigQueryUtils.getDatasetLocation(config);
      final BigQuery bigquery = getBigQuery(config);
      final UploadingMethod uploadingMethod = getLoadingMethod(config);

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

  // https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html
  private Integer getBigQueryClientChunkSize(final JsonNode config) {
    Integer chunkSizeFromConfig = null;
    if (config.has(BigQueryConsts.BIG_QUERY_CLIENT_CHUNK_SIZE)) {
      chunkSizeFromConfig = config.get(BigQueryConsts.BIG_QUERY_CLIENT_CHUNK_SIZE).asInt();
      if (chunkSizeFromConfig <= 0) {
        LOGGER.error("BigQuery client Chunk (buffer) size must be a positive number (MB), but was:" + chunkSizeFromConfig);
        throw new IllegalArgumentException("BigQuery client Chunk (buffer) size must be a positive number (MB)");
      }
      chunkSizeFromConfig = chunkSizeFromConfig * BigQueryConsts.MiB;
    }
    return chunkSizeFromConfig;
  }

  private BigQuery getBigQuery(final JsonNode config) {
    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    try {
      final BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
      ServiceAccountCredentials credentials = null;
      if (isUsingJsonCredentials(config)) {
        // handle the credentials json being passed as a json object or a json object already serialized as
        // a string.
        final String credentialsString =
            config.get(BigQueryConsts.CONFIG_CREDS).isObject() ? Jsons.serialize(config.get(BigQueryConsts.CONFIG_CREDS))
                : config.get(BigQueryConsts.CONFIG_CREDS).asText();
        credentials = ServiceAccountCredentials
            .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
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

  public static boolean isUsingJsonCredentials(final JsonNode config) {
    return config.has(BigQueryConsts.CONFIG_CREDS) && !config.get(BigQueryConsts.CONFIG_CREDS).asText().isEmpty();
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
    final BigQuery bigquery = getBigQuery(config);
    final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs = new HashMap<>();
    final Set<String> existingSchemas = new HashSet<>();
    final boolean isGcsUploadingMode = UploadingMethod.GCS.equals(getLoadingMethod(config));
    final boolean isKeepFilesInGcs = isKeepFilesInGcs(config);

    // create tmp tables if not exist
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      final String streamName = stream.getName();
      final String schemaName = getSchema(config, configStream);
      final String tableName = getTargetTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final String datasetLocation = BigQueryUtils.getDatasetLocation(config);
      BigQueryUtils.createSchemaAndTableIfNeeded(bigquery, existingSchemas, schemaName, tmpTableName,
          datasetLocation, getBigQuerySchema(stream.getJsonSchema()));
      final Schema schema = getBigQuerySchema(stream.getJsonSchema());
      // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
      final WriteChannelConfiguration writeChannelConfiguration = WriteChannelConfiguration
          .newBuilder(TableId.of(schemaName, tmpTableName))
          .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
          .setSchema(schema)
          .setFormatOptions(FormatOptions.json()).build(); // new-line delimited json.

      final JobId job = JobId.newBuilder()
          .setRandomJob()
          .setLocation(datasetLocation)
          .setProject(bigquery.getOptions().getProjectId())
          .build();

      final TableDataWriteChannel writer = bigquery.writer(job, writeChannelConfiguration);

      // this this optional value. If not set - use default client's value (15MiG)
      final Integer bigQueryClientChunkSizeFomConfig = getBigQueryClientChunkSize(config);
      if (bigQueryClientChunkSizeFomConfig != null) {
        writer.setChunkSize(bigQueryClientChunkSizeFomConfig);
      }
      final WriteDisposition syncMode = getWriteDisposition(configStream.getDestinationSyncMode());

      if (isGcsUploadingMode) {
        final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
            .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(config));
        final GcsCsvWriter gcsCsvWriter = initGcsWriter(gcsDestinationConfig, configStream);
        gcsCsvWriter.initialize();

        writeConfigs.put(AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
            new BigQueryWriteConfig(TableId.of(schemaName, tableName), TableId.of(schemaName, tmpTableName),
                writer, syncMode, schema, gcsCsvWriter, gcsDestinationConfig));
      } else {
        writeConfigs.put(AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
            new BigQueryWriteConfig(TableId.of(schemaName, tableName), TableId.of(schemaName, tmpTableName),
                writer, syncMode, schema, null, null));
      }

    }
    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return getRecordConsumer(bigquery, writeConfigs, catalog, outputRecordCollector, isGcsUploadingMode, isKeepFilesInGcs);
  }

  /**
   * Despite the fact that uploading to going to be done to GCS, you may see the S3 client
   * initialization. The S3 client appears to be compatible with GCS and widely used in
   * destination-gcs connector. Since the destination-gcs connector is partially re-used here - we
   * also need to init S3 client.
   *
   * @param gcsDestinationConfig
   * @param configuredStream
   * @return GcsCsvWriter
   * @throws IOException
   */
  private GcsCsvWriter initGcsWriter(final GcsDestinationConfig gcsDestinationConfig,
                                     final ConfiguredAirbyteStream configuredStream)
      throws IOException {
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
    return new GcsCsvWriter(gcsDestinationConfig, s3Client, configuredStream, uploadTimestamp);
  }

  protected String getTargetTableName(final String streamName) {
    return namingResolver.getRawTableName(streamName);
  }

  protected AirbyteMessageConsumer getRecordConsumer(final BigQuery bigquery,
                                                     final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                                     final ConfiguredAirbyteCatalog catalog,
                                                     final Consumer<AirbyteMessage> outputRecordCollector,
                                                     final boolean isGcsUploadingMode,
                                                     final boolean isKeepFilesInGcs) {
    return new BigQueryRecordConsumer(bigquery, writeConfigs, catalog, outputRecordCollector, isGcsUploadingMode, isKeepFilesInGcs);
  }

  protected Schema getBigQuerySchema(final JsonNode jsonSchema) {
    return SCHEMA;
  }

  private static String getSchema(final JsonNode config, final ConfiguredAirbyteStream stream) {
    final String defaultSchema = config.get(BigQueryConsts.CONFIG_DATASET_ID).asText();
    final String srcNamespace = stream.getStream().getNamespace();
    if (srcNamespace == null) {
      return defaultSchema;
    }
    return srcNamespace;
  }

  private static WriteDisposition getWriteDisposition(final DestinationSyncMode syncMode) {
    if (syncMode == null) {
      throw new IllegalStateException("Undefined destination sync mode");
    }
    switch (syncMode) {
      case OVERWRITE -> {
        return WriteDisposition.WRITE_TRUNCATE;
      }
      case APPEND, APPEND_DEDUP -> {
        return WriteDisposition.WRITE_APPEND;
      }
      default -> throw new IllegalStateException("Unrecognized destination sync mode: " + syncMode);
    }
  }

  private UploadingMethod getLoadingMethod(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    if (loadingMethod != null && BigQueryConsts.GCS_STAGING.equals(loadingMethod.get(BigQueryConsts.METHOD).asText())) {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.GCS);
      return UploadingMethod.GCS;
    } else {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.STANDARD);
      return UploadingMethod.STANDARD;
    }
  }

  private boolean isKeepFilesInGcs(final JsonNode config) {
    final JsonNode loadingMethod = config.get(BigQueryConsts.LOADING_METHOD);
    if (loadingMethod != null && loadingMethod.get(BigQueryConsts.KEEP_GCS_FILES) != null
        && BigQueryConsts.KEEP_GCS_FILES_VAL
            .equals(loadingMethod.get(BigQueryConsts.KEEP_GCS_FILES).asText())) {
      LOGGER.info("All tmp files GCS will be kept in bucket when replication is finished");
      return true;
    } else {
      LOGGER.info("All tmp files will be removed from GCS when replication is finished");
      return false;
    }
  }

  public enum UploadingMethod {
    STANDARD,
    GCS
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    LOGGER.info("starting destination: {}", BigQueryDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BigQueryDestination.class);
  }

}
