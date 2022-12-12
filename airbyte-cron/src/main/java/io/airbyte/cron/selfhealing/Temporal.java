/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import static io.airbyte.cron.MicronautCronRunner.SCHEDULED_TRACE_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.temporal.TemporalClient;
import io.micronaut.scheduling.annotation.Scheduled;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class Temporal {

  private final TemporalClient temporalClient;

  public Temporal(final TemporalClient temporalClient) {
    log.debug("Creating temporal self-healing");
    this.temporalClient = temporalClient;
  }

  @Trace(operationName = SCHEDULED_TRACE_OPERATION_NAME)
  @Scheduled(fixedRate = "10s")
  void cleanTemporal() {
    temporalClient.restartClosedWorkflowByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
  }

}
