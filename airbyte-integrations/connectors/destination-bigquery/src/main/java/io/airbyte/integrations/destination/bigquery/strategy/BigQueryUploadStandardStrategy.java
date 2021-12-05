/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.strategy;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
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
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploadStandardStrategy implements BigQueryUploadStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploadStandardStrategy.class);

  private final BigQuery bigquery;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  public BigQueryUploadStandardStrategy(BigQuery bigquery,
                                        ConfiguredAirbyteCatalog catalog,
                                        Consumer<AirbyteMessage> outputRecordCollector) {
    this.bigquery = bigquery;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  public void upload(BigQueryWriteConfig writer, AirbyteMessage airbyteMessage, ConfiguredAirbyteCatalog catalog) {
    try {
      writer.getWriter()
          .write(ByteBuffer.wrap((Jsons.serialize(formatRecord(writer.getSchema(), airbyteMessage.getRecord())) + "\n").getBytes(Charsets.UTF_8)));
    } catch (final IOException | RuntimeException e) {
      LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
      LOGGER.error(String.format(
          "Failed to process a message for job: %s, \nStreams numbers: %s, \nSyncMode: %s, \nTableName: %s, \nTmpTableName: %s, \nAirbyteMessage: %s",
          writer.getWriter().getJob(), catalog.getStreams().size(), writer.getSyncMode(), writer.getTable(), writer.getTmpTable(),
          airbyteMessage.getRecord()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
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

  @Override
  public void close(List<BigQueryWriteConfig> writeConfigList, boolean hasFailed, AirbyteMessage lastStateMessage) {
    try {
      writeConfigList.parallelStream().forEach(bigQueryWriteConfig -> Exceptions.toRuntime(() -> {
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
      writeConfigList.forEach(bigQueryWriteConfig -> Exceptions.toRuntime(() -> {
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
        writeConfigList
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
      writeConfigList.forEach(bigQueryWriteConfig -> bigquery.delete(bigQueryWriteConfig.getTmpTable()));
      LOGGER.info("Finishing destination process...completed");
    }
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
