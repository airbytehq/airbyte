/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
public class StreamResetActivityImpl implements StreamResetActivity {

  private final StreamResetRecordsHelper streamResetRecordsHelper;

  public StreamResetActivityImpl(final StreamResetRecordsHelper streamResetRecordsHelper) {
    this.streamResetRecordsHelper = streamResetRecordsHelper;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void deleteStreamResetRecordsForJob(final DeleteStreamResetRecordsForJobInput input) {
    ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, input.getConnectionId(), JOB_ID_KEY, input.getJobId()));
    streamResetRecordsHelper.deleteStreamResetRecordsForJob(input.getJobId(), input.getConnectionId());
  }

}
