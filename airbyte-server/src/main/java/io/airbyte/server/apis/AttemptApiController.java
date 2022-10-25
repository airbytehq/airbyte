/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.AttemptApi;
import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.handlers.AttemptHandler;
import javax.ws.rs.Path;

@Path("/v1/attempt/set_workflow_in_attempt")
public class AttemptApiController implements AttemptApi {

  private final AttemptHandler attemptHandler;

  public AttemptApiController(final JobPersistence jobPersistence) {
    attemptHandler = new AttemptHandler(jobPersistence);
  }

  @Override
  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody requestBody) {
    return ConfigurationApi.execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

}
