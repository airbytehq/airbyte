/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobConfiguration;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobStatistics;
import com.google.cloud.bigquery.JobStatus;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableResult;
import com.google.common.collect.Streams;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.math.BigInteger;
import java.time.Instant;
import java.util.Comparator;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO this stuff almost definitely exists somewhere else in our codebase.
public class BigQueryDestinationHandler implements DestinationHandler<TableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationHandler.class);

  private final BigQuery bq;
  private final String datasetLocation;

  public BigQueryDestinationHandler(final BigQuery bq, final String datasetLocation) {
    this.bq = bq;
    this.datasetLocation = datasetLocation;
  }

  @Override
  public Optional<TableDefinition> findExistingTable(final StreamId id) {
    final Table table = bq.getTable(id.finalNamespace(), id.finalName());
    return Optional.ofNullable(table).map(Table::getDefinition);
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) {
    return BigInteger.ZERO.equals(bq.getTable(TableId.of(id.finalNamespace(), id.finalName())).getNumRows());
  }

  @Override
  public Optional<Instant> getMinTimestampForSync(final StreamId id) throws Exception {
    final Table rawTable = bq.getTable(TableId.of(id.rawNamespace(), id.rawName()));
    if (rawTable == null) {
      return Optional.empty();
    }
    final TableResult queryResult = bq.query(QueryJobConfiguration.newBuilder(new StringSubstitutor(Map.of(
        "raw_table", id.rawTableId(BigQuerySqlGenerator.QUOTE))).replace(
            // bigquery timestamps have microsecond precision
            // and COALESCE short-circuits, so if the first subquery returns non-null, we don't
            // evaluate the second query at all
            """
            SELECT COALESCE(
              (
                SELECT TIMESTAMP_SUB(MIN(_airbyte_extracted_at), INTERVAL 1 MICROSECOND)
                FROM ${raw_table}
                WHERE _airbyte_loaded_at IS NULL
              ),
              (
                SELECT MAX(_airbyte_extracted_at)
                FROM ${raw_table}
              )
            )
            """))
        .build());
    final FieldValue value = queryResult.iterateAll().iterator().next().get(0);
    if (value.isNull()) {
      return Optional.empty();
    } else {
      return Optional.ofNullable(value.getTimestampInstant());
    }
  }

  @Override
  public void execute(final String sql) throws InterruptedException {
    if ("".equals(sql)) {
      return;
    }
    final UUID queryId = UUID.randomUUID();
    LOGGER.info("Executing sql {}: {}", queryId, sql);

    /*
     * If you run a query like CREATE SCHEMA ... OPTIONS(location=foo); CREATE TABLE ...;, bigquery
     * doesn't do a good job of inferring the query location. Pass it in explicitly.
     */
    Job job = bq.create(JobInfo.of(JobId.newBuilder().setLocation(datasetLocation).build(), QueryJobConfiguration.newBuilder(sql).build()));
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
    LOGGER.info("Root-level job {} completed in {} ms; processed {} bytes; billed for {} bytes",
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
              LOGGER.info("Child sql {} completed in {} ms; processed {} bytes; billed for {} bytes",
                  truncatedQuery,
                  childQueryStats.getEndTime() - childQueryStats.getStartTime(),
                  childQueryStats.getTotalBytesProcessed(),
                  childQueryStats.getTotalBytesBilled());
            } else {
              // other job types are extract/copy/load
              // we're probably not using them, but handle just in case?
              final JobStatistics childJobStats = childJob.getStatistics();
              LOGGER.info("Non-query child job ({}) completed in {} ms",
                  configuration.getType(),
                  childJobStats.getEndTime() - childJobStats.getStartTime());
            }
          });
    }
  }

}
