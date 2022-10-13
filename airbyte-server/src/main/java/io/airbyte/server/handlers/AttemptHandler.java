/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AttemptHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AttemptHandler.class);

  private final JobPersistence jobPersistence;

  public AttemptHandler(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  public InternalOperationResult setWorkflowInAttempt(
                                                      SetWorkflowInAttemptRequestBody requestBody) {
    try {
      jobPersistence.setAttemptTemporalWorkflowId(requestBody.getJobId(),
          requestBody.getAttemptNumber(), requestBody.getWorkflowId().toString());
    } catch (IOException ioe) {
      LOGGER.error("IOException when setting temporal workflow in attempt;", ioe);
      return new InternalOperationResult().succeeded(false);
    }
    return new InternalOperationResult().succeeded(true);
  }

}
