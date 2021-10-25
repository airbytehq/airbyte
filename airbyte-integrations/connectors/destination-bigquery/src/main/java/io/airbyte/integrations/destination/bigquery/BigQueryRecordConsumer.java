/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static com.amazonaws.util.StringUtils.UTF8;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.CsvOptions;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.nio.ByteBuffer;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final boolean isGcsUploadingMode;
  private final boolean isKeepFilesInGcs;

  private AirbyteMessage lastStateMessage = null;

  public BigQueryRecordConsumer(final BigQuery bigquery,
                                final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                final ConfiguredAirbyteCatalog catalog,
                                final Consumer<AirbyteMessage> outputRecordCollector,
                                final boolean isGcsUploadingMode,
                                final boolean isKeepFilesInGcs) {
    this.bigquery = bigquery;
    this.writeConfigs = writeConfigs;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.isGcsUploadingMode = isGcsUploadingMode;
    this.isKeepFilesInGcs = isKeepFilesInGcs;
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  public void acceptTracked(final AirbyteMessage message) throws IOException {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
    } else if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();

      // ignore other message types.
      final AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
      }
      final BigQueryWriteConfig writer = writeConfigs.get(pair);

      // select the way of uploading - normal or through the GCS
      if (writer.getGcsCsvWriter() == null) {
        // Normal uploading way
        try {
          writer.getWriter()
              .write(ByteBuffer.wrap((Jsons.serialize(formatRecord(writer.getSchema(), recordMessage)) + "\n").getBytes(Charsets.UTF_8)));
        } catch (final IOException | RuntimeException e) {
          LOGGER.error("Got an error while writing message:" + e.getMessage());
          LOGGER.error(String.format(
              "Failed to process a message for job: %s, \nStreams numbers: %s, \nSyncMode: %s, \nTableName: %s, \nTmpTableName: %s, \nAirbyteMessage: %s",
              writer.getWriter().getJob(), catalog.getStreams().size(), writer.getSyncMode(), writer.getTable(), writer.getTmpTable(), message));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      } else {
        // GCS uploading way, this data will be moved to bigquery in close method
        final GcsCsvWriter gcsCsvWriter = writer.getGcsCsvWriter();
        writeRecordToCsv(gcsCsvWriter, recordMessage);
      }
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }
  }

  protected JsonNode formatRecord(final Schema schema, final AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(formattedData),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
  }

  protected void writeRecordToCsv(final GcsCsvWriter gcsCsvWriter, final AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    try {
      gcsCsvWriter.getCsvPrinter().printRecord(
          UUID.randomUUID().toString(),
          formattedEmittedAt,
          Jsons.serialize(formattedData));
    } catch (IOException e) {
      e.printStackTrace();
      LOGGER.warn("An error occurred writing CSV file.");
    }
  }

  @Override
  public void close(final boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    // process gcs streams
    if (isGcsUploadingMode) {
      closeGcsStreamsAndCopyDataToBigQuery(hasFailed);
    }

    closeNormalBigqueryStreams(hasFailed);

    if (isGcsUploadingMode && !isKeepFilesInGcs) {
      deleteDataFromGcsBucket();
    }
  }

  private void closeGcsStreamsAndCopyDataToBigQuery(final boolean hasFailed) {
    final List<BigQueryWriteConfig> gcsWritersList = writeConfigs.values().parallelStream()
        .filter(el -> el.getGcsCsvWriter() != null)
        .collect(Collectors.toList());

    if (!gcsWritersList.isEmpty()) {
      LOGGER.info("GCS connectors that need to be closed:" + gcsWritersList);
      gcsWritersList.parallelStream().forEach(writer -> {
        final GcsCsvWriter gcsCsvWriter = writer.getGcsCsvWriter();

        try {
          LOGGER.info("Closing connector:" + gcsCsvWriter);
          gcsCsvWriter.close(hasFailed);
        } catch (final IOException | RuntimeException e) {
          LOGGER.error(String.format("Failed to close %s gcsWriter, \n details: %s", gcsCsvWriter, e.getMessage()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      });
    }

    // copy data from tmp gcs storage to bigquery tables
    writeConfigs.values().stream()
        .filter(pair -> pair.getGcsCsvWriter() != null)
        .forEach(pair -> {
          try {
            loadCsvFromGcsTruncate(pair);
          } catch (final Exception e) {
            LOGGER.error("Failed to load data from GCS CSV file to BigQuery tmp table with reason: " + e.getMessage());
            throw new RuntimeException(e);
          }
        });
  }

  private void loadCsvFromGcsTruncate(final BigQueryWriteConfig bigQueryWriteConfig)
      throws Exception {
    try {

      final TableId tmpTable = bigQueryWriteConfig.getTmpTable();
      final Schema schema = bigQueryWriteConfig.getSchema();

      final String csvFile = bigQueryWriteConfig.getGcsCsvWriter().getGcsCsvFileLocation();

      // Initialize client that will be used to send requests. This client only needs to be created
      // once, and can be reused for multiple requests.
      LOGGER.info(String.format("Started copying data from %s GCS csv file to %s tmp BigQuery table with schema: \n %s",
          csvFile, tmpTable, schema));

      final CsvOptions csvOptions = CsvOptions.newBuilder().setEncoding(UTF8).setSkipLeadingRows(1).build();

      final LoadJobConfiguration configuration =
          LoadJobConfiguration.builder(tmpTable, csvFile)
              .setFormatOptions(csvOptions)
              .setSchema(schema)
              .setWriteDisposition(bigQueryWriteConfig.getSyncMode())
              .build();

      // For more information on Job see:
      // https://googleapis.dev/java/google-cloud-clients/latest/index.html?com/google/cloud/bigquery/package-summary.html
      // Load the table
      final Job loadJob = bigquery.create(JobInfo.of(configuration));

      LOGGER.info("Created a new job GCS csv file to tmp BigQuery table: " + loadJob);
      LOGGER.info("Waiting for job to complete...");

      // Load data from a GCS parquet file into the table
      // Blocks until this load table job completes its execution, either failing or succeeding.
      final Job completedJob = loadJob.waitFor();

      // Check for errors
      if (completedJob == null) {
        LOGGER.error("Job not executed since it no longer exists.");
        throw new Exception("Job not executed since it no longer exists.");
      } else if (completedJob.getStatus().getError() != null) {
        // You can also look at queryJob.getStatus().getExecutionErrors() for all
        // errors, not just the latest one.
        final String msg = "BigQuery was unable to load into the table due to an error: \n"
            + loadJob.getStatus().getError();
        LOGGER.error(msg);
        throw new Exception(msg);
      }
      LOGGER.info("Table is successfully overwritten by CSV file loaded from GCS");
    } catch (final BigQueryException | InterruptedException e) {
      LOGGER.error("Column not added during load append \n" + e.toString());
      throw new RuntimeException("Column not added during load append \n" + e.toString());
    }
  }

  private void closeNormalBigqueryStreams(final boolean hasFailed) {
    try {
      writeConfigs.values().parallelStream().forEach(bigQueryWriteConfig -> Exceptions.toRuntime(() -> {
        final TableDataWriteChannel writer = bigQueryWriteConfig.getWriter();
        try {
          writer.close();
        } catch (final IOException | RuntimeException e) {
          LOGGER.error(String.format("Failed to close writer: %s, \nStreams numbers: %s",
              writer.getJob(), catalog.getStreams().size()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
      }));

      LOGGER.info("Waiting for jobs to be finished/closed");
      writeConfigs.values().forEach(bigQueryWriteConfig -> Exceptions.toRuntime(() -> {
        if (bigQueryWriteConfig.getWriter().getJob() != null) {
          try {
            bigQueryWriteConfig.getWriter().getJob().waitFor();
          } catch (final RuntimeException e) {
            LOGGER.error(
                String.format("Failed to process a message for job: %s, \nStreams numbers: %s, \nSyncMode: %s, \nTableName: %s, \nTmpTableName: %s",
                    bigQueryWriteConfig.getWriter().getJob(), catalog.getStreams().size(), bigQueryWriteConfig.getSyncMode(),
                    bigQueryWriteConfig.getTable(), bigQueryWriteConfig.getTmpTable()));
            printHeapMemoryConsumption();
            throw new RuntimeException(e);
          }
        }
      }));

      if (!hasFailed) {
        LOGGER.info("Replication finished with no explicit errors. Copying data from tmp tables to permanent");
        writeConfigs.values()
            .forEach(
                bigQueryWriteConfig -> {
                  if (bigQueryWriteConfig.getSyncMode().equals(WriteDisposition.WRITE_APPEND)) {
                    partitionIfUnpartitioned(bigQueryWriteConfig, bigquery, bigQueryWriteConfig.getTable());
                  }
                  copyTable(bigquery, bigQueryWriteConfig.getTmpTable(), bigQueryWriteConfig.getTable(),
                      bigQueryWriteConfig.getSyncMode());
                });
        // BQ is still all or nothing if a failure happens in the destination.
        outputRecordCollector.accept(lastStateMessage);
      } else {
        LOGGER.warn("Had errors while replicating");
      }
    } finally {
      // clean up tmp tables;
      LOGGER.info("Removing tmp tables...");
      writeConfigs.values().forEach(bigQueryWriteConfig -> bigquery.delete(bigQueryWriteConfig.getTmpTable()));
      LOGGER.info("Finishing destination process...completed");
    }
  }

  private void deleteDataFromGcsBucket() {
    writeConfigs.values().forEach(writeConfig -> {
      final GcsDestinationConfig gcsDestinationConfig = writeConfig.getGcsDestinationConfig();
      final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

      final String gcsBucketName = gcsDestinationConfig.getBucketName();
      final String gcs_bucket_path = gcsDestinationConfig.getBucketPath();

      final List<KeyVersion> keysToDelete = new LinkedList<>();
      final List<S3ObjectSummary> objects = s3Client
          .listObjects(gcsBucketName, gcs_bucket_path)
          .getObjectSummaries();
      for (final S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (keysToDelete.size() > 0) {
        LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
        // Google Cloud Storage doesn't accept request to delete multiple objects
        for (final KeyVersion keyToDelete : keysToDelete) {
          s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
        }
        LOGGER.info("Deleted {} file(s).", keysToDelete.size());
      }
      s3Client.shutdown();
    });
  }

  // https://cloud.google.com/bigquery/docs/managing-tables#copying_a_single_source_table
  private static void copyTable(
                                final BigQuery bigquery,
                                final TableId sourceTableId,
                                final TableId destinationTableId,
                                final WriteDisposition syncMode) {
    final CopyJobConfiguration configuration = CopyJobConfiguration.newBuilder(destinationTableId, sourceTableId)
        .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
        .setWriteDisposition(syncMode)
        .build();

    final Job job = bigquery.create(JobInfo.of(configuration));
    final ImmutablePair<Job, String> jobStringImmutablePair = BigQueryUtils.executeQuery(job);
    if (jobStringImmutablePair.getRight() != null) {
      LOGGER.error("Failed on copy tables with error:" + job.getStatus());
      throw new RuntimeException("BigQuery was unable to copy table due to an error: \n" + job.getStatus().getError());
    }
    LOGGER.info("successfully copied table: {} to table: {}", sourceTableId, destinationTableId);
  }

  private void partitionIfUnpartitioned(final BigQueryWriteConfig bigQueryWriteConfig,
                                        final BigQuery bigquery,
                                        final TableId destinationTableId) {
    try {
      final QueryJobConfiguration queryConfig = QueryJobConfiguration
          .newBuilder(
              String.format("SELECT max(is_partitioning_column) as is_partitioned FROM `%s.%s.INFORMATION_SCHEMA.COLUMNS` WHERE TABLE_NAME = '%s';",
                  bigquery.getOptions().getProjectId(),
                  destinationTableId.getDataset(),
                  destinationTableId.getTable()))
          .setUseLegacySql(false)
          .build();
      final ImmutablePair<Job, String> result = BigQueryUtils.executeQuery(bigquery, queryConfig);
      result.getLeft().getQueryResults().getValues().forEach(row -> {
        if (!row.get("is_partitioned").isNull() && row.get("is_partitioned").getStringValue().equals("NO")) {
          LOGGER.info("Partitioning existing destination table {}", destinationTableId);
          final String tmpPartitionTable = Strings.addRandomSuffix("_airbyte_partitioned_table", "_", 5);
          final TableId tmpPartitionTableId = TableId.of(destinationTableId.getDataset(), tmpPartitionTable);
          // make sure tmpPartitionTable does not already exist
          bigquery.delete(tmpPartitionTableId);
          // Use BigQuery SQL to copy because java api copy jobs does not support creating a table from a
          // select query, see:
          // https://cloud.google.com/bigquery/docs/creating-partitioned-tables#create_a_partitioned_table_from_a_query_result
          final QueryJobConfiguration partitionQuery = QueryJobConfiguration
              .newBuilder(
                  getCreatePartitionedTableFromSelectQuery(bigQueryWriteConfig.getSchema(), bigquery.getOptions().getProjectId(), destinationTableId,
                      tmpPartitionTable))
              .setUseLegacySql(false)
              .build();
          BigQueryUtils.executeQuery(bigquery, partitionQuery);
          // Copying data from a partitioned tmp table into an existing non-partitioned table does not make it
          // partitioned... thus, we force re-create from scratch by completely deleting and creating new
          // table.
          bigquery.delete(destinationTableId);
          copyTable(bigquery, tmpPartitionTableId, destinationTableId, WriteDisposition.WRITE_EMPTY);
          bigquery.delete(tmpPartitionTableId);
        }
      });
    } catch (final InterruptedException e) {
      LOGGER.warn("Had errors while partitioning: ", e);
    }
  }

  protected String getCreatePartitionedTableFromSelectQuery(final Schema schema,
                                                            final String projectId,
                                                            final TableId destinationTableId,
                                                            final String tmpPartitionTable) {
    return String.format("create table `%s.%s.%s` (", projectId, destinationTableId.getDataset(), tmpPartitionTable)
        + schema.getFields().stream()
            .map(field -> String.format("%s %s", field.getName(), field.getType()))
            .collect(Collectors.joining(", "))
        + ") partition by date("
        + JavaBaseConstants.COLUMN_NAME_EMITTED_AT
        + ") as select "
        + schema.getFields().stream()
            .map(Field::getName)
            .collect(Collectors.joining(", "))
        + String.format(" from `%s.%s.%s`", projectId, destinationTableId.getDataset(), destinationTableId.getTable());
  }

  private void printHeapMemoryConsumption() {
    final int mb = 1024 * 1024;
    final MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
    final long xmx = memoryBean.getHeapMemoryUsage().getMax() / mb;
    final long xms = memoryBean.getHeapMemoryUsage().getInit() / mb;
    LOGGER.info("Initial Memory (xms) mb = " + xms);
    LOGGER.info("Max Memory (xmx) : mb + " + xmx);
  }

}
