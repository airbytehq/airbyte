/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.JOBS;
import static org.jooq.impl.SQLDataType.VARCHAR;

import io.airbyte.db.instance.configs.jooq.generated.enums.StatusType;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import jakarta.inject.Singleton;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.jooq.DSLContext;

@Singleton
class MetricRepository {

  private final DSLContext ctx;

  MetricRepository(final DSLContext ctx) {
    this.ctx = ctx;
  }

  int numberOfPendingJobs() {
    return ctx.selectCount()
        .from(JOBS)
        .where(JOBS.STATUS.eq(JobStatus.pending))
        .fetchOne(0, int.class);
  }

  int numberOfRunningJobs() {
    return ctx.selectCount()
        .from(JOBS)
        .join(CONNECTION)
        .on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.STATUS.eq(JobStatus.running).and(CONNECTION.STATUS.eq(StatusType.active)))
        .fetchOne(0, int.class);
  }

  int numberOfOrphanRunningJobs() {
    return ctx.selectCount()
        .from(JOBS)
        .join(CONNECTION)
        .on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.STATUS.eq(JobStatus.running).and(CONNECTION.STATUS.ne(StatusType.active)))
        .fetchOne(0, int.class);
  }

  long oldestPendingJobAgeSecs() {
    return oldestJobAgeSecs(JobStatus.pending);
  }

  long oldestRunningJobAgeSecs() {
    return oldestJobAgeSecs(JobStatus.running);
  }

  List<Long> numberOfActiveConnPerWorkspace() {
    final var query = """
                      SELECT workspace_id, count(c.id) as num_conn
                      FROM actor
                        INNER JOIN workspace ws ON actor.workspace_id = ws.id
                        INNER JOIN connection c ON actor.id = c.source_id
                      WHERE ws.tombstone = false
                        AND actor.tombstone = false AND actor.actor_type = 'source'
                        AND c.status = 'active'
                      GROUP BY workspace_id;
                      """;
    return ctx.fetch(query).getValues("num_conn", long.class);
  }

  long numScheduledActiveConnectionsInLastDay() {
    final var queryForTotalConnections = """
                                         select count(1) as connection_count
                                         from connection c
                                         where
                                           c.updated_at < now() - interval '24 hours 1 minutes'
                                           and cast(c.schedule::jsonb->'timeUnit' as text) IN ('"hours"', '"minutes"')
                                           and c.status = 'active'
                                         """;

    return ctx.fetchOne(queryForTotalConnections).get("connection_count", long.class);
  }

  long numberOfJobsNotRunningOnScheduleInLastDay() {
    // This query finds all sync jobs ran in last 24 hours and count how many times they have run.
    // Comparing this to the expected number of runs (24 hours divide by configured cadence in hours),
    // if it runs below that expected number it will be considered as abnormal instance.
    // For example, if it's configured to run every 6 hours but in last 24 hours it only has 3 runs,
    // it will be considered as 1 abnormal instance.
    final var queryForAbnormalSyncInHoursInLastDay = """
                                                     select count(1) as cnt
                                                     from (
                                                       select
                                                         c.id,
                                                         count(*) as cnt
                                                       from connection c
                                                       left join jobs j on j.scope::uuid = c.id
                                                       where
                                                         c.schedule is not null
                                                         and c.schedule != 'null'
                                                         and j.created_at > now() - interval '24 hours 1 minutes'
                                                         and c.status = 'active'
                                                         and j.config_type = 'sync'
                                                         and c.updated_at < now() - interval '24 hours 1 minutes'
                                                         and cast(c.schedule::jsonb->'timeUnit' as text) = '"hours"'
                                                       group by 1
                                                       having count(*) < 24 / cast(c.schedule::jsonb->'units' as integer)
                                                     ) as abnormal_jobs
                                                     """;

    // Similar to the query above, this finds if the connection cadence's timeUnit is minutes.
    // thus we use 1440 (=24 hours x 60 minutes) to divide the configured cadence.
    final var queryForAbnormalSyncInMinutesInLastDay = """
                                                       select count(1) as cnt
                                                       from (
                                                         select
                                                           c.id,
                                                           count(*) as cnt
                                                         from
                                                           connection c
                                                         left join Jobs j on
                                                           j.scope::uuid = c.id
                                                         where
                                                           c.schedule is not null
                                                           and c.schedule != 'null'
                                                           and j.created_at > now() - interval '24 hours 1 minutes'
                                                           and c.status = 'active'
                                                           and j.config_type = 'sync'
                                                           and c.updated_at < now() - interval '24 hours 1 minutes'
                                                           and cast(c.schedule::jsonb->'timeUnit' as text) = '"minutes"'
                                                         group by 1
                                                         having count(*) < 1440 / cast(c.schedule::jsonb->'units' as integer)
                                                       ) as abnormal_jobs
                                                       """;
    return ctx.fetchOne(queryForAbnormalSyncInHoursInLastDay).get("cnt", long.class)
        + ctx.fetchOne(queryForAbnormalSyncInMinutesInLastDay).get("cnt", long.class);
  }

  Map<JobStatus, Double> overallJobRuntimeForTerminalJobsInLastHour() {
    final var query = """
                      SELECT status, extract(epoch from age(updated_at, created_at)) AS sec FROM jobs
                      WHERE updated_at >= NOW() - INTERVAL '1 HOUR'
                        AND (jobs.status = 'failed' OR jobs.status = 'succeeded' OR jobs.status = 'cancelled');
                      """;
    final var statuses = ctx.fetch(query).getValues("status", JobStatus.class);
    final var times = ctx.fetch(query).getValues("sec", double.class);

    final var results = new HashMap<JobStatus, Double>();
    for (int i = 0; i < statuses.size(); i++) {
      results.put(statuses.get(i), times.get(i));
    }

    return results;
  }

  private long oldestJobAgeSecs(final JobStatus status) {
    final var readableTimeField = "run_duration";
    final var durationSecField = "run_duration_secs";
    final var query = String.format("""
                                    WITH
                                    oldest_job AS (
                                    SELECT id,
                                           age(current_timestamp, created_at) AS %s
                                    FROM jobs
                                    WHERE status = '%s'
                                    ORDER BY run_duration DESC
                                    LIMIT 1)
                                    SELECT id,
                                           run_duration,
                                           extract(epoch from run_duration) as %s
                                    FROM oldest_job""", readableTimeField, status.getLiteral(), durationSecField);
    final var res = ctx.fetch(query);
    // unfortunately there are no good Jooq methods for retrieving a single record of a single column
    // forcing the List cast.
    final var duration = res.getValues(durationSecField, Double.class);

    if (duration.size() == 0) {
      return 0L;
    }

    // as double can have rounding errors, round down to remove noise.
    return duration.get(0).longValue();
  }

}
