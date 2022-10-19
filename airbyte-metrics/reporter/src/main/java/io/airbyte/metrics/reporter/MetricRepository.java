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

  long numberOfJobsRunningUnusuallyLong() {
    // Definition of unusually long means runtime is more than 2x historic avg run time or 15
    // minutes more than avg run time, whichever is greater.
    // It will skip jobs with fewer than 4 runs in last week to make sure the historic avg run is
    // meaningful and consistent.
    final var query =
        """
        -- pick average running time and last sync running time in attempts table.
          select
            current_running_attempts.connection_id,
            current_running_attempts.running_time,
            historic_avg_running_attempts.avg_run_sec
            from
            	(
             -- Sub-query-1: query the currently running attempt's running time.
                (
                  select
                    jobs.scope as connection_id,
                    extract(epoch from age(NOW(), attempts.created_at)) as running_time
                  from
                    jobs
                  join attempts on
                    jobs.id = attempts.job_id
                  where
                    jobs.status = 'running'
                    and attempts.status = 'running'
                    and jobs.config_type = 'sync' )
                        as current_running_attempts
              join
            -- Sub-query-2: query historic attempts' average running time within last week.
                (
                  select
                    jobs.scope as connection_id,
                    avg(extract(epoch from age(attempts.updated_at, attempts.created_at))) as avg_run_sec
                  from
                    jobs
                  join attempts on
                    jobs.id = attempts.job_id
                  where
                  -- 168 hours is 1 week: we look for all attempts in last week to calculate its average running time.
                    attempts.updated_at >= NOW() - interval '168 HOUR'
                    and jobs.status = 'succeeded'
                    and attempts.status = 'succeeded'
                    and jobs.config_type = 'sync'
                  group by
                    connection_id
                  having
                    count(*) > 4
                ) as historic_avg_running_attempts
              on
                current_running_attempts.connection_id = historic_avg_running_attempts.connection_id)
          where
          -- Find if currently running time takes 2x more time than average running time,
          -- and it's 15 minutes (900 seconds) more than average running time so it won't alert on noises for quick sync jobs.
            current_running_attempts.running_time > greatest(historic_avg_running_attempts.avg_run_sec * 2, historic_avg_running_attempts.avg_run_sec + 900)
        """;
    final var queryResults = ctx.fetch(query);
    return queryResults.getValues("connection_id").size();
  }

  Map<JobStatus, Double> overallJobRuntimeForTerminalJobsInLastHour() {
    final var query = """
                      SELECT status, extract(epoch from age(updated_at, created_at)) AS sec FROM jobs
                      WHERE updated_at >= NOW() - INTERVAL '1 HOUR'
                        AND jobs.status IN ('failed', 'succeeded', 'cancelled');
                      """;
    final var queryResults = ctx.fetch(query);
    final var statuses = queryResults.getValues("status", JobStatus.class);
    final var times = queryResults.getValues("sec", double.class);

    final var results = new HashMap<JobStatus, Double>();
    for (int i = 0; i < statuses.size(); i++) {
      results.put(statuses.get(i), times.get(i));
    }

    return results;
  }

  private long oldestJobAgeSecs(final JobStatus status) {
    final var query = """
                      SELECT id, EXTRACT(EPOCH FROM (current_timestamp - created_at)) AS run_duration_seconds
                      FROM jobs WHERE status = ?::job_status
                      ORDER BY created_at ASC limit 1;
                      """;
    final var result = ctx.fetchOne(query, status.getLiteral());
    if (result == null) {
      return 0L;
    }
    // as double can have rounding errors, round down to remove noise.
    return result.getValue("run_duration_seconds", Double.class).longValue();
  }

}
