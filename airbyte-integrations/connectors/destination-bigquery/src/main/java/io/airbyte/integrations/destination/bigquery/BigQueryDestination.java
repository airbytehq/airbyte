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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.WriteChannelConfiguration;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream.DestinationSyncMode;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestination.class);
  static final String CONFIG_DATASET_ID = "dataset_id";
  static final String CONFIG_PROJECT_ID = "project_id";
  static final String CONFIG_CREDS = "credentials_json";

  static final com.google.cloud.bigquery.Schema SCHEMA = com.google.cloud.bigquery.Schema.of(
      Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
      Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));

  private final StandardNameTransformer namingResolver;

  public BigQueryDestination() {
    namingResolver = new StandardNameTransformer();
  }

  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a jsonschema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      final String datasetId = config.get(CONFIG_DATASET_ID).asText();
      final BigQuery bigquery = getBigQuery(config);
      createSchemaTable(bigquery, datasetId);
      QueryJobConfiguration queryConfig = QueryJobConfiguration
          .newBuilder(String.format("SELECT * FROM %s.INFORMATION_SCHEMA.TABLES LIMIT 1;", datasetId))
          .setUseLegacySql(false)
          .build();

      final ImmutablePair<Job, String> result = executeQuery(bigquery, queryConfig);
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

  private void createSchemaTable(BigQuery bigquery, String datasetId) {
    final Dataset dataset = bigquery.getDataset(datasetId);
    if (dataset == null || !dataset.exists()) {
      final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).build();
      bigquery.create(datasetInfo);
    }
  }

  private BigQuery getBigQuery(JsonNode config) {
    final String projectId = config.get(CONFIG_PROJECT_ID).asText();
    // handle the credentials json being passed as a json object or a json object already serialized as
    // a string.
    final String credentialsString =
        config.get(CONFIG_CREDS).isObject() ? Jsons.serialize(config.get(CONFIG_CREDS)) : config.get(CONFIG_CREDS).asText();
    try {
      final ServiceAccountCredentials credentials = ServiceAccountCredentials
          .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));

      return BigQueryOptions.newBuilder()
          .setProjectId(projectId)
          .setCredentials(credentials)
          .build()
          .getService();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  static ImmutablePair<Job, String> executeQuery(BigQuery bigquery, QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  private static ImmutablePair<Job, String> executeQuery(Job queryJob) {
    final Job completedJob = waitForQuery(queryJob);
    if (completedJob == null) {
      throw new RuntimeException("Job no longer exists");
    } else if (completedJob.getStatus().getError() != null) {
      // You can also look at queryJob.getStatus().getExecutionErrors() for all
      // errors, not just the latest one.
      return ImmutablePair.of(null, (completedJob.getStatus().getError().toString()));
    }

    return ImmutablePair.of(completedJob, null);
  }

  private static Job waitForQuery(Job queryJob) {
    try {
      return queryJob.waitFor();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
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
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) {
    final BigQuery bigquery = getBigQuery(config);
    Map<String, WriteConfig> writeConfigs = new HashMap<>();
    final String datasetId = config.get(CONFIG_DATASET_ID).asText();
    Set<String> schemaSet = new HashSet<>();

    // create tmp tables if not exist
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = namingResolver.getIdentifier(datasetId);
      final String tableName = namingResolver.getRawTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      if (!schemaSet.contains(schemaName)) {
        createSchemaTable(bigquery, schemaName);
        schemaSet.add(schemaName);
      }
      createTable(bigquery, schemaName, tmpTableName);

      // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
      final WriteChannelConfiguration writeChannelConfiguration = WriteChannelConfiguration
          .newBuilder(TableId.of(schemaName, tmpTableName))
          .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
          .setSchema(SCHEMA)
          .setFormatOptions(FormatOptions.json()).build(); // new-line delimited json.

      final TableDataWriteChannel writer = bigquery.writer(JobId.of(UUID.randomUUID().toString()), writeChannelConfiguration);
      final WriteDisposition syncMode = getWriteDisposition(stream.getDestinationSyncMode());

      writeConfigs.put(stream.getStream().getName(),
          new WriteConfig(TableId.of(schemaName, tableName), TableId.of(schemaName, tmpTableName), writer, syncMode));
    }

    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return new RecordConsumer(bigquery, writeConfigs, catalog);
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

  // https://cloud.google.com/bigquery/docs/tables#create-table
  private static void createTable(BigQuery bigquery, String datasetName, String tableName) {
    try {

      final TableId tableId = TableId.of(datasetName, tableName);
      final TableDefinition tableDefinition = StandardTableDefinition.of(SCHEMA);
      final TableInfo tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build();

      bigquery.create(tableInfo);
      LOGGER.info("Table created successfully");
    } catch (BigQueryException e) {
      LOGGER.info("Table was not created. \n" + e.toString());
    }
  }

  // https://cloud.google.com/bigquery/docs/managing-tables#copying_a_single_source_table
  private static void copyTable(
                                BigQuery bigquery,
                                TableId sourceTableId,
                                TableId destinationTableId,
                                WriteDisposition syncMode) {

    final CopyJobConfiguration configuration = CopyJobConfiguration.newBuilder(destinationTableId, sourceTableId)
        .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
        .setWriteDisposition(syncMode)
        .build();

    final Job job = bigquery.create(JobInfo.of(configuration));
    final ImmutablePair<Job, String> jobStringImmutablePair = executeQuery(job);
    if (jobStringImmutablePair.getRight() != null) {
      throw new RuntimeException("BigQuery was unable to copy table due to an error: \n" + job.getStatus().getError());
    }
  }

  public static class RecordConsumer extends FailureTrackingAirbyteMessageConsumer {

    private final BigQuery bigquery;
    private final Map<String, WriteConfig> writeConfigs;
    private final ConfiguredAirbyteCatalog catalog;

    public RecordConsumer(BigQuery bigquery, Map<String, WriteConfig> writeConfigs, ConfiguredAirbyteCatalog catalog) {
      this.bigquery = bigquery;
      this.writeConfigs = writeConfigs;
      this.catalog = catalog;
    }

    @Override
    protected void startTracked() {
      // todo (cgardens) - move contents of #write into this method.
    }

    @Override
    public void acceptTracked(AirbyteMessage message) {
      // ignore other message types.
      if (message.getType() == AirbyteMessage.Type.RECORD) {
        if (!writeConfigs.containsKey(message.getRecord().getStream())) {
          throw new IllegalArgumentException(
              String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                  Jsons.serialize(catalog), Jsons.serialize(message)));
        }

        // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
        // use BQ helpers to string-format correctly.
        long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(message.getRecord().getEmittedAt(), TimeUnit.MILLISECONDS);
        final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();

        final JsonNode data = Jsons.jsonNode(ImmutableMap.of(
            JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
            JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(message.getRecord().getData()),
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
        try {
          writeConfigs.get(message.getRecord().getStream()).getWriter()
              .write(ByteBuffer.wrap((Jsons.serialize(data) + "\n").getBytes(Charsets.UTF_8)));
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      }
    }

    @Override
    public void close(boolean hasFailed) {
      try {
        writeConfigs.values().parallelStream().forEach(writeConfig -> Exceptions.toRuntime(() -> writeConfig.getWriter().close()));
        writeConfigs.values().forEach(writeConfig -> Exceptions.toRuntime(() -> {
          if (writeConfig.getWriter().getJob() != null) {
            writeConfig.getWriter().getJob().waitFor();
          }
        }));
        if (!hasFailed) {
          LOGGER.error("executing on success close procedure.");
          writeConfigs.values()
              .forEach(writeConfig -> copyTable(bigquery, writeConfig.getTmpTable(), writeConfig.getTable(), writeConfig.getSyncMode()));
        }
      } finally {
        // clean up tmp tables;
        writeConfigs.values().forEach(writeConfig -> bigquery.delete(writeConfig.getTmpTable()));
      }
    }

  }

  private static class WriteConfig {

    private final TableId table;
    private final TableId tmpTable;
    private final TableDataWriteChannel writer;
    private final WriteDisposition syncMode;

    private WriteConfig(TableId table, TableId tmpTable, TableDataWriteChannel writer, WriteDisposition syncMode) {
      this.table = table;
      this.tmpTable = tmpTable;
      this.writer = writer;
      this.syncMode = syncMode;
    }

    public TableId getTable() {
      return table;
    }

    public TableId getTmpTable() {
      return tmpTable;
    }

    public TableDataWriteChannel getWriter() {
      return writer;
    }

    public WriteDisposition getSyncMode() {
      return syncMode;
    }

  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new BigQueryDestination();
    LOGGER.info("starting destination: {}", BigQueryDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", BigQueryDestination.class);
  }

}
