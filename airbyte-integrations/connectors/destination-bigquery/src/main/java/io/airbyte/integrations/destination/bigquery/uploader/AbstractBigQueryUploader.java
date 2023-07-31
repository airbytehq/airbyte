/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.s3.writer.DestinationWriter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.io.IOException;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractBigQueryUploader<T extends DestinationWriter> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractBigQueryUploader.class);

  protected final TableId table;
  protected final TableId tmpTable;
  protected final WriteDisposition syncMode;
  protected final T writer;
  protected final BigQuery bigQuery;
  protected final BigQueryRecordFormatter recordFormatter;
  protected final boolean use1s1t;

  AbstractBigQueryUploader(final TableId table,
                           final TableId tmpTable,
                           final T writer,
                           final WriteDisposition syncMode,
                           final BigQuery bigQuery,
                           final BigQueryRecordFormatter recordFormatter) {
    this.use1s1t = TypingAndDedupingFlag.isDestinationV2();
    this.table = table;
    this.tmpTable = tmpTable;
    this.writer = writer;
    this.syncMode = syncMode;
    this.bigQuery = bigQuery;
    this.recordFormatter = recordFormatter;
  }

  public BigQueryRecordFormatter getRecordFormatter() {
    return recordFormatter;
  }

  protected void postProcessAction(final boolean hasFailed) throws Exception {
    // Do nothing by default
  }

  public void upload(final AirbyteMessage airbyteMessage) {
    try {
      writer.write(recordFormatter.formatRecord(airbyteMessage.getRecord()));
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

  public void close(final boolean hasFailed, final Consumer<AirbyteMessage> outputRecordCollector, final AirbyteMessage lastStateMessage) {
    try {
      recordFormatter.printAndCleanFieldFails();

      LOGGER.info("Closing connector: {}", this);
      this.writer.close(hasFailed);

      if (!hasFailed) {
        uploadData(outputRecordCollector, lastStateMessage);
      }
      this.postProcessAction(hasFailed);
      LOGGER.info("Closed connector: {}", this);
    } catch (final Exception e) {
      LOGGER.error(String.format("Failed to close %s writer, \n details: %s", this, e.getMessage()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  protected void uploadData(final Consumer<AirbyteMessage> outputRecordCollector, final AirbyteMessage lastStateMessage) throws Exception {
    try {
      if (!use1s1t) {
        // This only needs to happen if we actually wrote to a tmp table.
        LOGGER.info("Uploading data from the tmp table {} to the source table {}.", tmpTable.getTable(), table.getTable());
        uploadDataToTableFromTmpTable();
        LOGGER.info("Data is successfully loaded to the source table {}!", table.getTable());
      }

      outputRecordCollector.accept(lastStateMessage);
      LOGGER.info("Final state message is accepted.");
    } catch (final Exception e) {
      LOGGER.error("Upload data is failed!");
      throw e;
    } finally {
      dropTmpTable();
    }
  }

  public void createRawTable() {
    // Ensure that this table exists.
    // TODO alter an existing raw table?
    final Table rawTable = bigQuery.getTable(table);
    if (rawTable == null) {
      LOGGER.info("Creating raw table {}.", table);
      bigQuery.create(TableInfo.newBuilder(table, StandardTableDefinition.of(recordFormatter.getBigQuerySchema())).build());
    } else {
      LOGGER.info("Found raw table {}.", rawTable.getTableId());
    }
  }

  protected void dropTmpTable() {
    try {
      // clean up tmp tables;
      LOGGER.info("Removing tmp tables...");
      bigQuery.delete(tmpTable);
      LOGGER.info("Finishing destination process...completed");
    } catch (final Exception e) {
      LOGGER.error("Fail to tmp table drop table: " + e.getMessage());
    }
  }

  protected void uploadDataToTableFromTmpTable() {
    LOGGER.info("Replication finished with no explicit errors. Copying data from tmp tables to permanent");
    if (syncMode.equals(JobInfo.WriteDisposition.WRITE_APPEND)) {
      partitionIfUnpartitioned(bigQuery, recordFormatter.getBigQuerySchema(), table);
    }
    copyTable(bigQuery, tmpTable, table, syncMode);
  }

  /**
   * Creates a partitioned table if the table previously was not partitioned
   *
   * <p>
   * Note: this logic is deprecated since it was used for the functionality of migrating unpartitioned
   * tables to partitioned tables for performance. Since this change was introduced in Oct 2021 there
   * is a well founded belief that any customer's that would have ran a sync in between end of 2022
   * and Oct 2021 would have migrated to a partition table
   * </p>
   *
   * @param bigQuery BigQuery interface
   * @param schema Schema of the data table
   * @param destinationTableId identifier for a table
   */
  @Deprecated
  public static void partitionIfUnpartitioned(final BigQuery bigQuery, final Schema schema, final TableId destinationTableId) {
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
                  getCreatePartitionedTableFromSelectQuery(schema, bigQuery.getOptions().getProjectId(),
                      destinationTableId,
                      tmpPartitionTable))
              .setUseLegacySql(false)
              .build();
          BigQueryUtils.executeQuery(bigQuery, partitionQuery);
          // Copying data from a partitioned tmp table into an existing non-partitioned table does not make it
          // partitioned... thus, we force re-create from scratch by completely deleting and creating new
          // table.
          bigQuery.delete(destinationTableId);
          copyTable(bigQuery, tmpPartitionTableId, destinationTableId, JobInfo.WriteDisposition.WRITE_EMPTY);
          bigQuery.delete(tmpPartitionTableId);
        }
      });
    } catch (final InterruptedException e) {
      LOGGER.warn("Had errors while partitioning: ", e);
    }
  }

  /**
   * Copies table from source to destination, while also creating the destination table if not already
   * existing
   * <p>
   * https://cloud.google.com/bigquery/docs/managing-tables#copying_a_single_source_table
   * </p>
   *
   * @param bigQuery BigQuery interface
   * @param sourceTableId source table
   * @param destinationTableId destination table
   * @param syncMode mapping of Airbyte's sync mode to BigQuery's write mode
   */
  public static void copyTable(final BigQuery bigQuery,
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

  private static String getCreatePartitionedTableFromSelectQuery(final Schema schema,
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

  @Override
  public String toString() {
    return "AbstractBigQueryUploader{" +
        "table=" + table.getTable() +
        ", tmpTable=" + tmpTable.getTable() +
        ", syncMode=" + syncMode +
        ", writer=" + writer.getClass() +
        ", recordFormatter=" + recordFormatter.getClass() +
        '}';
  }

}
