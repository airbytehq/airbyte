/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobConfiguration;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobStatistics;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.util.Comparator;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO this stuff almost definitely exists somewhere else in our codebase.
public class BigQueryDestinationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationHandler.class);

  private final BigQuery bq;

  public BigQueryDestinationHandler(final BigQuery bq) {
    this.bq = bq;
  }

  public Optional<TableDefinition> findExistingTable(StreamId id) {
    final Table table = bq.getTable(id.finalNamespace(), id.finalName());
    return Optional.ofNullable(table).map(Table::getDefinition);
  }

  public Table getFinalTable(StreamId id) {
    return bq.getTable(TableId.of(id.finalNamespace(), id.finalName()));
  }

  public void execute(final String sql) throws InterruptedException {
    if ("".equals(sql)) {
      return;
    }
    final UUID queryId = UUID.randomUUID();
    LOGGER.info("Executing sql {}: {}", queryId, sql);

    Job job = bq.create(JobInfo.of(QueryJobConfiguration.newBuilder(sql).build()));
    job = job.waitFor();
    // waitFor() seems to throw an exception, but javadoc says we're supposed to handle this case
    if (job.getStatus().getError() != null) {
      throw new RuntimeException(job.getStatus().getError().toString());
    }

    JobStatistics.QueryStatistics statistics = job.getStatistics();
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
            JobConfiguration configuration = childJob.getConfiguration();
            if (configuration instanceof QueryJobConfiguration qc) {
              JobStatistics.QueryStatistics childQueryStats = childJob.getStatistics();
              String truncatedQuery = qc.getQuery()
                  .substring(0, Math.min(100, qc.getQuery().length()))
                  .replaceAll("\n", " ");
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
              JobStatistics childJobStats = childJob.getStatistics();
              LOGGER.info("Non-query child job ({}) completed in {} ms",
                  configuration.getType(),
                  childJobStats.getEndTime() - childJobStats.getStartTime());
            }
          });
    }
  }

}
