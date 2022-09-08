/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.selfhealing;

import io.airbyte.workers.temporal.TemporalClient;
import io.micronaut.scheduling.annotation.Scheduled;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import javax.inject.Named;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class Temporal {

  private final TemporalClient temporalClient;

  public Temporal(@Named("temporalClient") final TemporalClient temporalClient) {
    log.info("Creating temporal self-healing");
    this.temporalClient = temporalClient;
  }

  @Scheduled(fixedRate = "10s")
  void cleanTemporal() {
    temporalClient.restartWorkflowByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
  }

}
