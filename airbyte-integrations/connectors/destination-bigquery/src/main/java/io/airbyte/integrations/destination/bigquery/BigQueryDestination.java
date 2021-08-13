/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.bigquery;

import static java.util.Objects.isNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
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
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
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
  private static final int MiB = 1024 * 1024;
  static final String CONFIG_DATASET_ID = "dataset_id";
  static final String CONFIG_PROJECT_ID = "project_id";
  static final String CONFIG_DATASET_LOCATION = "dataset_location";
  static final String CONFIG_CREDS = "credentials_json";
  static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";

  private static final com.google.cloud.bigquery.Schema SCHEMA = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));

  private final BigQuerySQLNameTransformer namingResolver;

  public BigQueryDestination() {
    namingResolver = new BigQuerySQLNameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      final String datasetId = config.get(CONFIG_DATASET_ID).asText();
      final String datasetLocation = getDatasetLocation(config);
      final BigQuery bigquery = getBigQuery(config);
      createSchemaTable(bigquery, datasetId, datasetLocation);
      QueryJobConfiguration queryConfig = QueryJobConfiguration
          .newBuilder(String.format("SELECT * FROM %s.INFORMATION_SCHEMA.TABLES LIMIT 1;", datasetId))
          .setUseLegacySql(false)
          .build();

      final ImmutablePair<Job, String> result = BigQueryUtils.executeQuery(bigquery, queryConfig);
      if (result.getLeft() != null) {
        return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
      } else {
        return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(result.getRight());
      }
    } catch (Exception e) {
      LOGGER.info("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  protected BigQuerySQLNameTransformer getNamingResolver() {
    return namingResolver;
  }

  private static String getDatasetLocation(JsonNode config) {
    if (config.has(CONFIG_DATASET_LOCATION)) {
      return config.get(CONFIG_DATASET_LOCATION).asText();
    } else {
      return "US";
    }
  }

  // https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html
  private Integer getBigQueryClientChunkSize(JsonNode config) {
    Integer chunkSizeFromConfig = null;
    if (config.has(BIG_QUERY_CLIENT_CHUNK_SIZE)) {
      chunkSizeFromConfig = config.get(BIG_QUERY_CLIENT_CHUNK_SIZE).asInt();
      if (chunkSizeFromConfig <= 0) {
        LOGGER.error("BigQuery client Chunk (buffer) size must be a positive number (MB), but was:" + chunkSizeFromConfig);
        throw new IllegalArgumentException("BigQuery client Chunk (buffer) size must be a positive number (MB)");
      }
      chunkSizeFromConfig = chunkSizeFromConfig * MiB;
    }
    return chunkSizeFromConfig;
  }

  private void createSchemaTable(BigQuery bigquery, String datasetId, String datasetLocation) {
    final Dataset dataset = bigquery.getDataset(datasetId);
    if (dataset == null || !dataset.exists()) {
      final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
      bigquery.create(datasetInfo);
    }
  }

  private BigQuery getBigQuery(JsonNode config) {
    final String projectId = config.get(CONFIG_PROJECT_ID).asText();

    try {
      BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
      ServiceAccountCredentials credentials = null;
      if (isUsingJsonCredentials(config)) {
        // handle the credentials json being passed as a json object or a json object already serialized as
        // a string.
        final String credentialsString =
            config.get(CONFIG_CREDS).isObject() ? Jsons.serialize(config.get(CONFIG_CREDS)) : config.get(CONFIG_CREDS).asText();
        credentials = ServiceAccountCredentials
            .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
      }
      return bigQueryBuilder
          .setProjectId(projectId)
          .setCredentials(!isNull(credentials) ? credentials : ServiceAccountCredentials.getApplicationDefault())
          .build()
          .getService();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static boolean isUsingJsonCredentials(JsonNode config) {
    return config.has(CONFIG_CREDS) && !config.get(CONFIG_CREDS).asText().isEmpty();
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
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    final BigQuery bigquery = getBigQuery(config);
    Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs = new HashMap<>();
    Set<String> existingSchemas = new HashSet<>();

    // create tmp tables if not exist
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      final String streamName = stream.getName();
      final String schemaName = getSchema(config, configStream);
      final String tableName = getTargetTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final String datasetLocation = getDatasetLocation(config);
      createSchemaAndTableIfNeeded(bigquery, existingSchemas, schemaName, tmpTableName, datasetLocation, stream.getJsonSchema());
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

      writeConfigs.put(AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
          new BigQueryWriteConfig(TableId.of(schemaName, tableName), TableId.of(schemaName, tmpTableName), writer, syncMode, schema));
    }
    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return getRecordConsumer(bigquery, writeConfigs, catalog, outputRecordCollector);
  }

  protected String getTargetTableName(String streamName) {
    return namingResolver.getRawTableName(streamName);
  }

  protected AirbyteMessageConsumer getRecordConsumer(BigQuery bigquery,
                                                     Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                                     ConfiguredAirbyteCatalog catalog,
                                                     Consumer<AirbyteMessage> outputRecordCollector) {
    return new BigQueryRecordConsumer(bigquery, writeConfigs, catalog, outputRecordCollector);
  }

  protected Schema getBigQuerySchema(JsonNode jsonSchema) {
    return SCHEMA;
  }

  private static String getSchema(JsonNode config, ConfiguredAirbyteStream stream) {
    final String defaultSchema = config.get(CONFIG_DATASET_ID).asText();
    final String srcNamespace = stream.getStream().getNamespace();
    if (srcNamespace == null) {
      return defaultSchema;
    }
    return srcNamespace;
  }

  private void createSchemaAndTableIfNeeded(BigQuery bigquery,
                                            Set<String> existingSchemas,
                                            String schemaName,
                                            String tmpTableName,
                                            String datasetLocation,
                                            JsonNode jsonSchema) {
    if (!existingSchemas.contains(schemaName)) {
      createSchemaTable(bigquery, schemaName, datasetLocation);
      existingSchemas.add(schemaName);
    }
    final Schema schema = getBigQuerySchema(jsonSchema);
    BigQueryUtils.createTable(bigquery, schemaName, tmpTableName, schema);
  }

  private static WriteDisposition getWriteDisposition(DestinationSyncMode syncMode) {
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

  public static void main(String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    LOGGER.info("starting destination: {}", BigQueryDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BigQueryDestination.class);
  }

}
