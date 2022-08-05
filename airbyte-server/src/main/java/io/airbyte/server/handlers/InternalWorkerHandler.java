/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SetTemporalWorkflowInAttemptRequestBody;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class InternalWorkerHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(InternalWorkerHandler.class);

  private final JobPersistence jobPersistence;

  public InternalWorkerHandler(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  public InternalOperationResult setTemporalWorkflowInAttempt(
                                                              SetTemporalWorkflowInAttemptRequestBody requestBody) {
    try {
      jobPersistence.setAttemptTemporalWorkflowId(requestBody.getJobId(),
          requestBody.getAttemptId().intValue(), requestBody.getTemporalWorkflowId().toString());
    } catch (IOException ioe) {
      LOGGER.error("IOException when setting temporal workflow in attempt;", ioe);
      return new InternalOperationResult().done(false);
    }
    return new InternalOperationResult().done(true);
  }

}
