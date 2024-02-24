/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsAllIgnoreCase;
import static io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsIgnoreCase;
import static io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.matchingKey;
import static io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator.QUOTE;
import static io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator.clusteringColumns;
import static io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator.toDialectType;
import static java.util.stream.Collectors.toMap;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobConfiguration;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobStatistics;
import com.google.cloud.bigquery.JobStatus;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Streams;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AlterTableReport;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialState;
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableState;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.apache.commons.text.StringSubstitutor;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO this stuff almost definitely exists somewhere else in our codebase.
public class BigQueryDestinationHandler implements DestinationHandler<BigqueryState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationHandler.class);

  private static final String DESTINATION_STATE_TABLE_NAME = "_airbyte_destination_state";
  private static final String DESTINATION_STATE_TABLE_COLUMN_NAME = "name";
  private static final String DESTINATION_STATE_TABLE_COLUMN_NAMESPACE = "namespace";
  private static final String DESTINATION_STATE_TABLE_COLUMN_STATE = "destination_state";
  private static final String DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT = "updated_at";

  private final BigQuery bq;
  private final String datasetLocation;
  private final String rawTableDataset;

  public BigQueryDestinationHandler(final BigQuery bq, final String datasetLocation, String rawTableDataset) {
    this.bq = bq;
    this.datasetLocation = datasetLocation;
    this.rawTableDataset = rawTableDataset;
  }

  public Optional<TableDefinition> findExistingTable(final StreamId id) {
    final Table table = bq.getTable(id.finalNamespace(), id.finalName());
    return Optional.ofNullable(table).map(Table::getDefinition);
  }

  public boolean isFinalTableEmpty(final StreamId id) {
    return BigInteger.ZERO.equals(bq.getTable(TableId.of(id.finalNamespace(), id.finalName())).getNumRows());
  }

  public InitialRawTableState getInitialRawTableState(final StreamId id) throws Exception {
    final Table rawTable = bq.getTable(TableId.of(id.rawNamespace(), id.rawName()));
    if (rawTable == null) {
      // Table doesn't exist. There are no unprocessed records, and no timestamp.
      return new InitialRawTableState(false, false, Optional.empty());
    }

    final FieldValue unloadedRecordTimestamp = bq.query(QueryJobConfiguration.newBuilder(new StringSubstitutor(Map.of(
        "raw_table", id.rawTableId(QUOTE))).replace(
            // bigquery timestamps have microsecond precision
            """
            SELECT TIMESTAMP_SUB(MIN(_airbyte_extracted_at), INTERVAL 1 MICROSECOND)
            FROM ${raw_table}
            WHERE _airbyte_loaded_at IS NULL
            """))
        .build()).iterateAll().iterator().next().get(0);
    // If this value is null, then there are no records with null loaded_at.
    // If it's not null, then we can return immediately - we've found some unprocessed records and their
    // timestamp.
    if (!unloadedRecordTimestamp.isNull()) {
      return new InitialRawTableState(true, true, Optional.of(unloadedRecordTimestamp.getTimestampInstant()));
    }

    final FieldValue loadedRecordTimestamp = bq.query(QueryJobConfiguration.newBuilder(new StringSubstitutor(Map.of(
        "raw_table", id.rawTableId(QUOTE))).replace(
            """
            SELECT MAX(_airbyte_extracted_at)
            FROM ${raw_table}
            """))
        .build()).iterateAll().iterator().next().get(0);
    // We know (from the previous query) that all records have been processed by T+D already.
    // So we just need to get the timestamp of the most recent record.
    if (loadedRecordTimestamp.isNull()) {
      // Null timestamp because the table is empty. T+D can process the entire raw table during this sync.
      return new InitialRawTableState(true, false, Optional.empty());
    } else {
      // The raw table already has some records. T+D can skip all records with timestamp <= this value.
      return new InitialRawTableState(true, false, Optional.of(loadedRecordTimestamp.getTimestampInstant()));
    }
  }

  @Override
  public void execute(final Sql sql) throws InterruptedException {
    final List<String> transactions = sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION");
    if (transactions.isEmpty()) {
      return;
    }
    final UUID queryId = UUID.randomUUID();
    final String statement = String.join("\n", transactions);
    LOGGER.debug("Executing sql {}: {}", queryId, statement);

    /*
     * If you run a query like CREATE SCHEMA ... OPTIONS(location=foo); CREATE TABLE ...;, bigquery
     * doesn't do a good job of inferring the query location. Pass it in explicitly.
     */
    Job job = bq.create(JobInfo.of(JobId.newBuilder().setLocation(datasetLocation).build(), QueryJobConfiguration.newBuilder(statement).build()));
    AirbyteExceptionHandler.addStringForDeinterpolation(job.getEtag());
    // job.waitFor() gets stuck forever in some failure cases, so manually poll the job instead.
    while (!JobStatus.State.DONE.equals(job.getStatus().getState())) {
      Thread.sleep(1000L);
      job = job.reload();
    }
    if (job.getStatus().getError() != null) {
      throw new BigQueryException(Streams.concat(
          Stream.of(job.getStatus().getError()),
          job.getStatus().getExecutionErrors().stream()).toList());
    }

    final JobStatistics.QueryStatistics statistics = job.getStatistics();
    LOGGER.debug("Root-level job {} completed in {} ms; processed {} bytes; billed for {} bytes",
        queryId,
        statistics.getEndTime() - statistics.getStartTime(),
        statistics.getTotalBytesProcessed(),
        statistics.getTotalBytesBilled());

    // SQL transactions can spawn child jobs, which are billed individually. Log their stats too.
    if (statistics.getNumChildJobs() != null) {
      // There isn't (afaict) anything resembling job.getChildJobs(), so we have to ask bq for them
      bq.listJobs(BigQuery.JobListOption.parentJobId(job.getJobId().getJob())).streamAll()
          .sorted(Comparator.comparing(childJob -> childJob.getStatistics().getEndTime()))
          .forEach(childJob -> {
            final JobConfiguration configuration = childJob.getConfiguration();
            if (configuration instanceof final QueryJobConfiguration qc) {
              final JobStatistics.QueryStatistics childQueryStats = childJob.getStatistics();
              String truncatedQuery = qc.getQuery()
                  .replaceAll("\n", " ")
                  .replaceAll(" +", " ")
                  .substring(0, Math.min(100, qc.getQuery().length()));
              if (!truncatedQuery.equals(qc.getQuery())) {
                truncatedQuery += "...";
              }
              LOGGER.debug("Child sql {} completed in {} ms; processed {} bytes; billed for {} bytes",
                  truncatedQuery,
                  childQueryStats.getEndTime() - childQueryStats.getStartTime(),
                  childQueryStats.getTotalBytesProcessed(),
                  childQueryStats.getTotalBytesBilled());
            } else {
              // other job types are extract/copy/load
              // we're probably not using them, but handle just in case?
              final JobStatistics childJobStats = childJob.getStatistics();
              LOGGER.debug("Non-query child job ({}) completed in {} ms",
                  configuration.getType(),
                  childJobStats.getEndTime() - childJobStats.getStartTime());
            }
          });
    }
  }

  @Override
  public List<DestinationInitialState<BigqueryState>> gatherInitialState(List<StreamConfig> streamConfigs) throws Exception {
    // Would be nice to use bq.create(), but it doesn't support `create table if not exists`.
    bq.query(QueryJobConfiguration.newBuilder(
        "CREATE TABLE IF NOT EXISTS " + getStateTableName() + " ("
            + DESTINATION_STATE_TABLE_COLUMN_NAME + " STRING, "
            + DESTINATION_STATE_TABLE_COLUMN_NAMESPACE + " STRING, "
            + DESTINATION_STATE_TABLE_COLUMN_STATE + " JSON, "
            + DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT + " TIMESTAMP)").build());

    Map<AirbyteStreamNameNamespacePair, BigqueryState> destinationStates = StreamSupport.stream(
        bq.query(QueryJobConfiguration.newBuilder(
            "SELECT * FROM " + getStateTableName()).build()).iterateAll().spliterator(),
        false).collect(
            toMap(
                fvList -> {
                  final FieldValue nameFieldValue = fvList.get(DESTINATION_STATE_TABLE_COLUMN_NAME);
                  final FieldValue namespaceFieldValue = fvList.get(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE);
                  return new AirbyteStreamNameNamespacePair(
                      nameFieldValue.isNull() ? null : nameFieldValue.getStringValue(),
                      namespaceFieldValue.isNull() ? null : namespaceFieldValue.getStringValue());
                },
                fvList -> {
                  JsonNode json = Jsons.deserialize(fvList.get(DESTINATION_STATE_TABLE_COLUMN_STATE).getStringValue());
                  return toBigqueryState(json);
                }));

    final List<DestinationInitialState<BigqueryState>> initialStates = new ArrayList<>();
    for (final StreamConfig streamConfig : streamConfigs) {
      final StreamId id = streamConfig.id();
      final Optional<TableDefinition> finalTable = findExistingTable(id);
      final InitialRawTableState rawTableState = getInitialRawTableState(id);
      final BigqueryState bigqueryState = destinationStates.getOrDefault(streamConfig.id().asPair(), toBigqueryState(Jsons.emptyObject()));
      initialStates.add(new DestinationInitialState<>(
          streamConfig,
          finalTable.isPresent(),
          rawTableState,
          finalTable.isPresent() && !existingSchemaMatchesStreamConfig(streamConfig, finalTable.get()),
          !finalTable.isPresent() || isFinalTableEmpty(id),
          bigqueryState));
    }
    return initialStates;
  }

  @Override
  public void commitDestinationStates(Map<StreamId, BigqueryState> destinationStates) throws Exception {
    if (destinationStates.isEmpty()) {
      return;
    }

    final String deleteStates = "DELETE FROM " + getStateTableName() + " WHERE "
        + destinationStates.keySet().stream()
            .map(streamId -> String.format("(%s = ? AND %s = ?)",
                DESTINATION_STATE_TABLE_COLUMN_NAME,
                DESTINATION_STATE_TABLE_COLUMN_NAMESPACE))
            .collect(Collectors.joining(" OR "));
    final QueryJobConfiguration.Builder deleteQueryConfig = QueryJobConfiguration.newBuilder(deleteStates);
    destinationStates.forEach((key, value) -> {
      deleteQueryConfig.addPositionalParameter(QueryParameterValue.string(key.originalName()));
      deleteQueryConfig.addPositionalParameter(QueryParameterValue.string(key.originalNamespace()));
    });
    bq.query(deleteQueryConfig.build());

    final String insertStates = "INSERT INTO " + getStateTableName() + " ("
        + DESTINATION_STATE_TABLE_COLUMN_NAME + ", "
        + DESTINATION_STATE_TABLE_COLUMN_NAMESPACE + ", "
        + DESTINATION_STATE_TABLE_COLUMN_STATE + ", "
        + DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT + ") VALUES "
        + destinationStates.keySet().stream()
            .map(streamId -> "(?, ?, ?, CURRENT_TIMESTAMP)")
            .collect(Collectors.joining(", "));
    final QueryJobConfiguration.Builder insertQueryConfig = QueryJobConfiguration.newBuilder(insertStates);
    destinationStates.forEach((key, value) -> {
      insertQueryConfig.addPositionalParameter(QueryParameterValue.string(key.originalName()));
      insertQueryConfig.addPositionalParameter(QueryParameterValue.string(key.originalNamespace()));
      insertQueryConfig.addPositionalParameter(QueryParameterValue.json(Jsons.serialize(value)));
    });
    bq.query(insertQueryConfig.build());
  }

  private boolean existingSchemaMatchesStreamConfig(final StreamConfig stream,
                                                    final TableDefinition existingTable)
      throws TableNotMigratedException {
    final var alterTableReport = buildAlterTableReport(stream, existingTable);
    boolean tableClusteringMatches = false;
    boolean tablePartitioningMatches = false;
    if (existingTable instanceof final StandardTableDefinition standardExistingTable) {
      tableClusteringMatches = clusteringMatches(stream, standardExistingTable);
      tablePartitioningMatches = partitioningMatches(standardExistingTable);
    }
    LOGGER.info("Alter Table Report {} {} {}; Clustering {}; Partitioning {}",
        alterTableReport.columnsToAdd(),
        alterTableReport.columnsToRemove(),
        alterTableReport.columnsToChangeType(),
        tableClusteringMatches,
        tablePartitioningMatches);

    return alterTableReport.isNoOp() && tableClusteringMatches && tablePartitioningMatches;
  }

  public AlterTableReport buildAlterTableReport(final StreamConfig stream, final TableDefinition existingTable) {
    final Set<String> pks = getPks(stream);

    final Map<String, StandardSQLTypeName> streamSchema = stream.columns().entrySet().stream()
        .collect(toMap(
            entry -> entry.getKey().name(),
            entry -> toDialectType(entry.getValue())));

    final Map<String, StandardSQLTypeName> existingSchema = existingTable.getSchema().getFields().stream()
        .collect(toMap(
            field -> field.getName(),
            field -> field.getType().getStandardType()));

    // Columns in the StreamConfig that don't exist in the TableDefinition
    final Set<String> columnsToAdd = streamSchema.keySet().stream()
        .filter(name -> !containsIgnoreCase(existingSchema.keySet(), name))
        .collect(Collectors.toSet());

    // Columns in the current schema that are no longer in the StreamConfig
    final Set<String> columnsToRemove = existingSchema.keySet().stream()
        .filter(name -> !containsIgnoreCase(streamSchema.keySet(), name) && !containsIgnoreCase(
            JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS, name))
        .collect(Collectors.toSet());

    // Columns that are typed differently than the StreamConfig
    final Set<String> columnsToChangeType = Stream.concat(
        streamSchema.keySet().stream()
            // If it's not in the existing schema, it should already be in the columnsToAdd Set
            .filter(name -> {
              // Big Query Columns are case-insensitive, first find the correctly cased key if it exists
              return matchingKey(existingSchema.keySet(), name)
                  // if it does exist, only include it in this set if the type (the value in each respective map)
                  // is different between the stream and existing schemas
                  .map(key -> !existingSchema.get(key).equals(streamSchema.get(name)))
                  // if there is no matching key, then don't include it because it is probably already in columnsToAdd
                  .orElse(false);
            }),

        // OR columns that used to have a non-null constraint and shouldn't
        // (https://github.com/airbytehq/airbyte/pull/31082)
        existingTable.getSchema().getFields().stream()
            .filter(field -> pks.contains(field.getName()))
            .filter(field -> field.getMode() == Field.Mode.REQUIRED)
            .map(Field::getName))
        .collect(Collectors.toSet());

    final boolean isDestinationV2Format = schemaContainAllFinalTableV2AirbyteColumns(existingSchema.keySet());

    return new AlterTableReport(columnsToAdd, columnsToRemove, columnsToChangeType, isDestinationV2Format);
  }

  @VisibleForTesting
  public static boolean clusteringMatches(final StreamConfig stream, final StandardTableDefinition existingTable) {
    return existingTable.getClustering() != null
        && containsAllIgnoreCase(
            new HashSet<>(existingTable.getClustering().getFields()),
            clusteringColumns(stream));
  }

  @VisibleForTesting
  public static boolean partitioningMatches(final StandardTableDefinition existingTable) {
    return existingTable.getTimePartitioning() != null
        && existingTable.getTimePartitioning()
            .getField()
            .equalsIgnoreCase("_airbyte_extracted_at")
        && TimePartitioning.Type.DAY.equals(existingTable.getTimePartitioning().getType());
  }

  /**
   * Checks the schema to determine whether the table contains all expected final table airbyte
   * columns
   *
   * @param columnNames the column names of the schema to check
   * @return whether all the {@link JavaBaseConstants#V2_FINAL_TABLE_METADATA_COLUMNS} are present
   */
  @VisibleForTesting
  public static boolean schemaContainAllFinalTableV2AirbyteColumns(final Collection<String> columnNames) {
    return JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.stream()
        .allMatch(column -> containsIgnoreCase(columnNames, column));
  }

  private static Set<String> getPks(final StreamConfig stream) {
    return stream.primaryKey() != null ? stream.primaryKey().stream().map(ColumnId::name).collect(Collectors.toSet()) : Collections.emptySet();
  }

  @NotNull
  private String getStateTableName() {
    return QUOTE + rawTableDataset + QUOTE + "." + DESTINATION_STATE_TABLE_NAME;
  }

  @NotNull
  private static BigqueryState toBigqueryState(JsonNode json) {
    return new BigqueryState(
        json.hasNonNull("needsSoftReset") && json.get("needsSoftReset").asBoolean());
  }

}
