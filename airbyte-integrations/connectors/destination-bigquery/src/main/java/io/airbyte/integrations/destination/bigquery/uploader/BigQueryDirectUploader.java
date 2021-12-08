package io.airbyte.integrations.destination.bigquery.uploader;

import com.google.cloud.bigquery.*;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.stream.Collectors;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

public class BigQueryDirectUploader extends AbstractBigQueryUploader<BigQueryTableWriter> {

    private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDirectUploader.class);

    public BigQueryDirectUploader(TableId table, TableId tmpTable, BigQueryTableWriter writer, JobInfo.WriteDisposition syncMode, Schema schema, GcsDestinationConfig gcsDestinationConfig, BigQuery bigQuery) {
        super(table, tmpTable, writer, syncMode, schema, gcsDestinationConfig, bigQuery);
    }

    @Override
    public void closeWriter(boolean hasFailed) throws Exception {
        try {
        writer.close(hasFailed);

        waitJobFinish();

        if (!hasFailed) {
            LOGGER.info("Replication finished with no explicit errors. Copying data from tmp tables to permanent");
            if (syncMode.equals(JobInfo.WriteDisposition.WRITE_APPEND)) {
                partitionIfUnpartitioned(table);
            }
            copyTable(tmpTable, table,
                    syncMode);

            // BQ is still all or nothing if a failure happens in the destination.
            outputRecordCollector.accept(lastStateMessage);
        } else {
            LOGGER.warn("Had errors while replicating");
        }
    } finally
    {
        // clean up tmp tables;
        LOGGER.info("Removing tmp tables...");
        bigQuery.delete(tmpTable);
        LOGGER.info("Finishing destination process...completed");
    }
}

    private void waitJobFinish() throws InterruptedException {
        var writeChannel = writer.getWriteChannel();
        var job = writeChannel.getJob();
        LOGGER.info("Waiting for jobs to be finished/closed");
        if (job != null) {
            try {
                job.waitFor();
            } catch (final RuntimeException e) {
                LOGGER.error(
                        String.format("Failed to process a message for job: %s",
                                job));
                printHeapMemoryConsumption();
                throw new RuntimeException(e);
            }
        }
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
