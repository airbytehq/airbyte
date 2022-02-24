/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;

import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;
import java.util.List;
import java.util.UUID;
import org.jooq.DSLContext;

/**
 * Keep track of all metric queries.
 */
public class MetricQueries {

  public static List<ReleaseStage> jobIdToReleaseStages(final DSLContext ctx, final long jobId) {
    final var srcRelStageCol = "src_release_stage";
    final var dstRelStageCol = "dst_release_stage";

    final var query = String.format("""
                                    select src_def_data.release_stage as %s,
                                           dest_def_data.release_stage as %s
                                    from connection
                                    inner join jobs on connection.id=CAST(jobs.scope AS uuid)
                                    inner join actor as dest_data on connection.destination_id = dest_data.id
                                    inner join actor_definition as dest_def_data on dest_data.actor_definition_id = dest_def_data.id
                                    inner join actor as src_data on connection.source_id = src_data.id
                                    inner join actor_definition as src_def_data on src_data.actor_definition_id = src_def_data.id
                                        where jobs.id = '%d';""", srcRelStageCol, dstRelStageCol, jobId);

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

}
