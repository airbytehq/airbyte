/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.jobs.jooq.Tables.JOBS;

import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;
import io.airbyte.db.instance.jobs.jooq.enums.JobStatus;
import java.util.List;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;

/**
 * Keep track of all metric queries.
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
    return ctx.selectCount().from(JOBS).where(JOBS.STATUS.eq(JobStatus.running)).fetchOne(0, int.class);
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
                                    with
                                    oldest_job as (
                                    SELECT id,
                                           age(current_timestamp, created_at) AS %s
                                    FROM jobs
                                    WHERE status = '%s'
                                    ORDER BY run_duration DESC
                                    LIMIT 1)
                                    select id,
                                           run_duration,
                                           extract(epoch from run_duration) as %s
                                    from oldest_job""", readableTimeField, status.getLiteral(), durationSecField);
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

}
