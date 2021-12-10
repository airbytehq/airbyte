/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.*;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.writer.CommonWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

public abstract class AbstractBigQueryUploader<T extends CommonWriter> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractBigQueryUploader.class);

  protected final TableId table;
  protected final TableId tmpTable;
  protected final WriteDisposition syncMode;
  protected final Schema schema;
  protected final T writer;
  protected final BigQuery bigQuery;

  AbstractBigQueryUploader(final TableId table,
                           final TableId tmpTable,
                           final T writer,
                           final WriteDisposition syncMode,
                           final Schema schema,
                           final BigQuery bigQuery) {
    this.table = table;
    this.tmpTable = tmpTable;
    this.writer = writer;
    this.syncMode = syncMode;
    this.schema = schema;
    this.bigQuery = bigQuery;
  }
  
  protected void postProcessAction(boolean hasFailed) throws Exception {
    // Do nothing by default
  }

  public void upload(AirbyteMessage airbyteMessage) {
    try {
      writer.write((formatRecord(airbyteMessage.getRecord())));
    } catch (final IOException | RuntimeException e) {
      LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
      LOGGER.error(String.format(
              "Failed to process a message for job: \n%s, \nAirbyteMessage: %s",
              writer.toString(),
              airbyteMessage.getRecord()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  protected JsonNode formatRecord(final AirbyteRecordMessage recordMessage) {
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

  public void close(boolean hasFailed, Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) {
        try {
          LOGGER.info("Closing connector:" + this);

          if (!hasFailed) {
            uploadData(outputRecordCollector, lastStateMessage);
          }
          this.postProcessAction(hasFailed);
          this.writer.close(hasFailed);
          LOGGER.info("Closed connector:" + this);
        } catch (final Exception e) {
          LOGGER.error(String.format("Failed to close %s writer, \n details: %s", this, e.getMessage()));
          printHeapMemoryConsumption();
          throw new RuntimeException(e);
        }
  }

  protected void uploadData(Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) throws Exception {
    try {
      LOGGER.info("Uploading data from the tmp table {} to the source table {}.", tmpTable.getTable(), table.getTable());
      uploadDataToTableFromTmpTable();
      LOGGER.info("Data is successfully loaded to the source table {}!", table.getTable());
      outputRecordCollector.accept(lastStateMessage);
      LOGGER.info("Final state message is accepted.");
    } catch (Exception e) {
      LOGGER.error("Upload data is failed!");
      throw e;
    } finally {
      dropTmpTable();
    }
  }

  protected void dropTmpTable() {
    try {
      // clean up tmp tables;
      LOGGER.info("Removing tmp tables...");
      //bigQuery.delete(tmpTable);
      LOGGER.info("Finishing destination process...completed");
    } catch (Exception e) {
      LOGGER.error("Fail to tmp table drop table: " + e.getMessage());
    }
  }

  protected void uploadDataToTableFromTmpTable() throws Exception {
    LOGGER.info("Replication finished with no explicit errors. Copying data from tmp tables to permanent");
    if (syncMode.equals(JobInfo.WriteDisposition.WRITE_APPEND)) {
      partitionIfUnpartitioned(table);
    }
    copyTable(tmpTable, table,
            syncMode);
  }

  private void partitionIfUnpartitioned(final TableId destinationTableId) {
    try {
      final QueryJobConfiguration queryConfig = QueryJobConfiguration
              .newBuilder(
                      String.format("SELECT max(is_partitioning_column) as is_partitioned FROM `%s.%s.INFORMATION_SCHEMA.COLUMNS` WHERE TABLE_NAME = '%s';",
                              bigQuery.getOptions().getProjectId(),
                              destinationTableId.getDataset(),
                              destinationTableId.getTable()))
              .setUseLegacySql(false)
              .build();
      final ImmutablePair<Job, String> result = BigQueryUtils.executeQuery(bigQuery, queryConfig);
      result.getLeft().getQueryResults().getValues().forEach(row -> {
        if (!row.get("is_partitioned").isNull() && row.get("is_partitioned").getStringValue().equals("NO")) {
          LOGGER.info("Partitioning existing destination table {}", destinationTableId);
          final String tmpPartitionTable = Strings.addRandomSuffix("_airbyte_partitioned_table", "_", 5);
          final TableId tmpPartitionTableId = TableId.of(destinationTableId.getDataset(), tmpPartitionTable);
          // make sure tmpPartitionTable does not already exist
          bigQuery.delete(tmpPartitionTableId);
          // Use BigQuery SQL to copy because java api copy jobs does not support creating a table from a
          // select query, see:
          // https://cloud.google.com/bigquery/docs/creating-partitioned-tables#create_a_partitioned_table_from_a_query_result
          final QueryJobConfiguration partitionQuery = QueryJobConfiguration
                  .newBuilder(
                          getCreatePartitionedTableFromSelectQuery(schema, bigQuery.getOptions().getProjectId(), destinationTableId,
                                  tmpPartitionTable))
                  .setUseLegacySql(false)
                  .build();
          BigQueryUtils.executeQuery(bigQuery, partitionQuery);
          // Copying data from a partitioned tmp table into an existing non-partitioned table does not make it
          // partitioned... thus, we force re-create from scratch by completely deleting and creating new
          // table.
          bigQuery.delete(destinationTableId);
          copyTable(tmpPartitionTableId, destinationTableId, JobInfo.WriteDisposition.WRITE_EMPTY);
          bigQuery.delete(tmpPartitionTableId);
        }
      });
    } catch (final InterruptedException e) {
      LOGGER.warn("Had errors while partitioning: ", e);
    }
  }

  // https://cloud.google.com/bigquery/docs/managing-tables#copying_a_single_source_table
  private void copyTable(
          final TableId sourceTableId,
          final TableId destinationTableId,
          final JobInfo.WriteDisposition syncMode) {
    final CopyJobConfiguration configuration = CopyJobConfiguration.newBuilder(destinationTableId, sourceTableId)
            .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
            .setWriteDisposition(syncMode)
            .build();

    final Job job = bigQuery.create(JobInfo.of(configuration));
    final ImmutablePair<Job, String> jobStringImmutablePair = BigQueryUtils.executeQuery(job);
    if (jobStringImmutablePair.getRight() != null) {
      LOGGER.error("Failed on copy tables with error:" + job.getStatus());
      throw new RuntimeException("BigQuery was unable to copy table due to an error: \n" + job.getStatus().getError());
    }
    LOGGER.info("successfully copied table: {} to table: {}", sourceTableId, destinationTableId);
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

}
