/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import io.airbyte.workers.temporal.TemporalClient;
import io.micronaut.scheduling.annotation.Scheduled;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class Temporal {

  @Inject
  private TemporalClient temporalClient;

  public Temporal() {
    log.info("Creating temporal self-healing");
  }

  @Scheduled(fixedRate = "10s")
  void cleanTemporal() {
    temporalClient.restartClosedWorkflowByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
  }

}
