/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.ATTEMPTS;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.JOBS;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.count;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.SQLDataType.VARCHAR;

import io.airbyte.db.instance.configs.jooq.generated.enums.StatusType;
import io.airbyte.db.instance.jobs.jooq.generated.enums.AttemptStatus;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import jakarta.inject.Singleton;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;

@Singleton
class MetricRepository {

  private final DSLContext ctx;

  // We have to report gauge metric with value 0 if they are not showing up in the DB,
  // otherwise datadog will use previous reported value.
  // Another option we didn't use here is to build this into SQL query - it will lead SQL much less
  // readable while not decreasing any complexity.
  private final static List<String> REGISTERED_ATTEMPT_QUEUE = List.of("SYNC", "AWS_PARIS_SYNC", "null");
  private final static List<String> REGISTERED_GEOGRAPHY = List.of("US", "AUTO", "EU");

  MetricRepository(final DSLContext ctx) {
    this.ctx = ctx;
  }

  Map<String, Integer> numberOfPendingJobsByGeography() {
    String geographyResultAlias = "geography";
    String countResultAlias = "result";
    var result = ctx.select(CONNECTION.GEOGRAPHY.cast(String.class).as(geographyResultAlias), count(asterisk()).as(countResultAlias))
        .from(JOBS)
        .join(CONNECTION)
        .on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.STATUS.eq(JobStatus.pending))
        .groupBy(CONNECTION.GEOGRAPHY);
    Field<String> geographyResultField = DSL.field(name(geographyResultAlias), String.class);
    Field<Integer> countResultField = DSL.field(name(countResultAlias), Integer.class);
    Map<String, Integer> queriedMap = result.fetchMap(geographyResultField, countResultField);
    for (final String potentialGeography : REGISTERED_GEOGRAPHY) {
      if (!queriedMap.containsKey(potentialGeography)) {
        queriedMap.put(potentialGeography, 0);
      }
    }
    return queriedMap;
  }

  Map<String, Integer> numberOfRunningJobsByTaskQueue() {
    String countFieldName = "count";
    var result = ctx.select(ATTEMPTS.PROCESSING_TASK_QUEUE, count(asterisk()).as(countFieldName))
        .from(JOBS)
        .join(CONNECTION)
        .on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .join(ATTEMPTS)
        .on(ATTEMPTS.JOB_ID.eq(JOBS.ID))
        .where(JOBS.STATUS.eq(JobStatus.running).and(CONNECTION.STATUS.eq(StatusType.active)))
        .and(ATTEMPTS.STATUS.eq(AttemptStatus.running))
        .groupBy(ATTEMPTS.PROCESSING_TASK_QUEUE);

    Field<Integer> countResultField = DSL.field(name(countFieldName), Integer.class);
    Map<String, Integer> queriedMap = result.fetchMap(ATTEMPTS.PROCESSING_TASK_QUEUE, countResultField);
    for (final String potentialAttemptQueue : REGISTERED_ATTEMPT_QUEUE) {
      if (!queriedMap.containsKey(potentialAttemptQueue)) {
        queriedMap.put(potentialAttemptQueue, 0);
      }
    }
    return queriedMap;
  }

  // This is a rare case and not likely to be related to data planes; So we will monitor them as a
  // whole.
  int numberOfOrphanRunningJobs() {
    return ctx.selectCount()
        .from(JOBS)
        .join(CONNECTION)
        .on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.STATUS.eq(JobStatus.running).and(CONNECTION.STATUS.ne(StatusType.active)))
        .fetchOne(0, int.class);
  }

  Map<String, Double> oldestPendingJobAgeSecsByGeography() {
    final var query =
        """
        SELECT cast(connection.geography as varchar) AS geography, MAX(EXTRACT(EPOCH FROM (current_timestamp - jobs.created_at))) AS run_duration_seconds
        FROM jobs
        JOIN connection
        ON jobs.scope::uuid = connection.id
        WHERE jobs.status = 'pending'
        GROUP BY geography;
        """;
    final var result = ctx.fetch(query);
    Field<String> geographyResultField = DSL.field(name("geography"), String.class);
    Field<Double> runDurationSecondsField = DSL.field(name("run_duration_seconds"), Double.class);
    Map<String, Double> queriedMap = result.intoMap(geographyResultField, runDurationSecondsField);
    for (final String potentialGeography : REGISTERED_GEOGRAPHY) {
      if (!queriedMap.containsKey(potentialGeography)) {
        queriedMap.put(potentialGeography, 0.0);
      }
    }
    return queriedMap;
  }

  Map<String, Double> oldestRunningJobAgeSecsByTaskQueue() {
    final var query =
        """
        SELECT attempts.processing_task_queue AS task_queue, MAX(EXTRACT(EPOCH FROM (current_timestamp - jobs.created_at))) AS run_duration_seconds
        FROM jobs
        JOIN attempts
        ON jobs.id = attempts.job_id
        WHERE jobs.status = 'running' AND attempts.status = 'running'
        GROUP BY task_queue;
        """;
    final var result = ctx.fetch(query);
    Field<String> taskQueueResultField = DSL.field(name("task_queue"), String.class);
    Field<Double> runDurationSecondsField = DSL.field(name("run_duration_seconds"), Double.class);
    Map<String, Double> queriedMap = result.intoMap(taskQueueResultField, runDurationSecondsField);
    for (final String potentialAttemptQueue : REGISTERED_ATTEMPT_QUEUE) {
      if (!queriedMap.containsKey(potentialAttemptQueue)) {
        queriedMap.put(potentialAttemptQueue, 0.0);
      }
    }
    return queriedMap;
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

}
