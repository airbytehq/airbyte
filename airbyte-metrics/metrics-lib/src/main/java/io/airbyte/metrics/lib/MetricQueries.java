/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.JOBS;
import static org.jooq.impl.SQLDataType.VARCHAR;

import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.db.instance.configs.jooq.generated.enums.StatusType;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.jooq.DSLContext;

/**
 * This class centralises metrics queries. These queries power metrics that require some sort of
 * data access or calculation.
 * <p>
 * Simple metrics that require no calculation need not be tracked here.
 */
@Slf4j
public class MetricQueries {

  public static List<ReleaseStage> jobIdToReleaseStages(final DSLContext ctx, final long jobId) {
    final var srcRelStageCol = "src_release_stage";
    final var dstRelStageCol = "dst_release_stage";

    final var query = String.format("""
                                    SELECT src_def_data.release_stage AS %s,
                                           dest_def_data.release_stage AS %s
                                    FROM connection
                                    INNER JOIN jobs ON connection.id=CAST(jobs.scope AS uuid)
                                    INNER JOIN actor AS dest_data ON connection.destination_id = dest_data.id
                                    INNER JOIN actor_definition AS dest_def_data ON dest_data.actor_definition_id = dest_def_data.id
                                    INNER JOIN actor AS src_data ON connection.source_id = src_data.id
                                    INNER JOIN actor_definition AS src_def_data ON src_data.actor_definition_id = src_def_data.id
                                        WHERE jobs.id = '%d';""", srcRelStageCol, dstRelStageCol, jobId);

    final var res = ctx.fetch(query);
    final var stages = res.getValues(srcRelStageCol, ReleaseStage.class);
    stages.addAll(res.getValues(dstRelStageCol, ReleaseStage.class));
    return stages;
  }

  public static List<ReleaseStage> srcIdAndDestIdToReleaseStages(final DSLContext ctx, final UUID srcId, final UUID dstId) {
    return ctx.select(ACTOR_DEFINITION.RELEASE_STAGE).from(ACTOR).join(ACTOR_DEFINITION).on(ACTOR.ACTOR_DEFINITION_ID.eq(ACTOR_DEFINITION.ID))
        .where(ACTOR.ID.eq(srcId))
        .or(ACTOR.ID.eq(dstId)).fetch().getValues(ACTOR_DEFINITION.RELEASE_STAGE);
  }

  public static int numberOfPendingJobs(final DSLContext ctx) {
    return ctx.selectCount().from(JOBS).where(JOBS.STATUS.eq(JobStatus.pending)).fetchOne(0, int.class);
  }

  public static int numberOfRunningJobs(final DSLContext ctx) {
    return ctx.selectCount().from(JOBS).join(CONNECTION).on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.STATUS.eq(JobStatus.running).and(CONNECTION.STATUS.eq(StatusType.active)))
        .fetchOne(0, int.class);
  }

  public static int numberOfOrphanRunningJobs(final DSLContext ctx) {
    return ctx.selectCount().from(JOBS).join(CONNECTION).on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.STATUS.eq(JobStatus.running).and(CONNECTION.STATUS.ne(StatusType.active)))
        .fetchOne(0, int.class);
  }

  public static Long oldestPendingJobAgeSecs(final DSLContext ctx) {
    return oldestJobAgeSecs(ctx, JobStatus.pending);
  }

  public static Long oldestRunningJobAgeSecs(final DSLContext ctx) {
    return oldestJobAgeSecs(ctx, JobStatus.running);
  }

  private static Long oldestJobAgeSecs(final DSLContext ctx, final JobStatus status) {
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
    // .get(0) works in the following code due to the query's SELECT 1.
    final var id = res.getValues("id", String.class).get(0);
    final var readableTime = res.getValues(readableTimeField, String.class).get(0);
    log.info("oldest job information - id: {}, readable time: {}", id, readableTime);

    // as double can have rounding errors, round down to remove noise.
    return duration.get(0).longValue();
  }

  public static List<Long> numberOfActiveConnPerWorkspace(final DSLContext ctx) {
    final var countField = "num_conn";
    final var query = String.format("""
                                    SELECT workspace_id, count(c.id) as %s
                                        FROM actor
                                            INNER JOIN workspace ws ON actor.workspace_id = ws.id
                                            INNER JOIN connection c ON actor.id = c.source_id
                                        WHERE ws.tombstone = false
                                          AND actor.tombstone = false AND actor.actor_type = 'source'
                                            AND c.status = 'active'
                                        GROUP BY workspace_id;""", countField);
    return ctx.fetch(query).getValues(countField, long.class);
  }

  public static List<Pair<JobStatus, Double>> overallJobRuntimeForTerminalJobsInLastHour(final DSLContext ctx) {
    final var statusField = "status";
    final var timeField = "sec";
    final var query =
        String.format("""
                      SELECT %s, extract(epoch from age(updated_at, created_at)) AS %s FROM jobs
                      WHERE updated_at >= NOW() - INTERVAL '1 HOUR'
                        AND (jobs.status = 'failed' OR jobs.status = 'succeeded' OR jobs.status = 'cancelled');""", statusField, timeField);
    final var statuses = ctx.fetch(query).getValues(statusField, JobStatus.class);
    final var times = ctx.fetch(query).getValues(timeField, double.class);

    final var pairedRes = new ArrayList<Pair<JobStatus, Double>>();
    for (int i = 0; i < statuses.size(); i++) {
      final var pair = new ImmutablePair<>(statuses.get(i), times.get(i));
      pairedRes.add(pair);
    }

    return pairedRes;
  }

  /*
   * A connection that is not running on schedule is defined in last 24 hours if the number of runs
   * are not matching with the number of expected runs according to the schedule settings. Refer to
   * playbook for detailed discussion.
   */
  public static Long numOfJobsNotRunningOnSchedule(final DSLContext ctx) {
    final var countField = "cnt";
    final var query = """
                      SELECT count(1) as cnt FROM ((
                      	SELECT
                      		c.id,
                      		count(*) as cnt
                      	FROM
                      		connection c
                      	LEFT JOIN Jobs j ON j.scope::uuid = c.id
                      	WHERE
                      		c.schedule IS NOT null
                      		AND c.schedule != 'null'
                      		AND j.created_at > now() - interval '24 hours 1 minutes'
                      		AND c.status = 'active'
                      		AND j.config_type = 'sync'
                      		AND c.updated_at < now() - interval '24 hours 1 minutes'
                      		AND cast(c.schedule::jsonb->'timeUnit' as text) = '"hours"'
                      	GROUP BY 1
                      	HAVING count(*) < 24 / cast(c.schedule::jsonb->'units' as integer))
                      UNION (
                      SELECT
                      	c.id,
                      	count(*) as cnt
                      FROM connection c
                      LEFT JOIN Jobs j ON j.scope::uuid = c.id
                      WHERE
                      	c.schedule IS NOT null
                      	AND c.schedule != 'null'
                      	AND j.created_at > now() - interval '1 hours 1 minutes'
                      	AND c.status = 'active'
                      	AND j.config_type = 'sync'
                      	AND c.updated_at < now() - interval '1 hours 1 minutes'
                      	AND cast(c.schedule::jsonb->'timeUnit' as text) = '"minutes"'
                      GROUP BY 1
                      HAVING count(*) < 60 / cast(c.schedule::jsonb->'units' as integer))) as abnormal_sync_jobs
                      	""";
    return ctx.fetch(query).getValues(countField, long.class).get(0).longValue();
  }

}
