/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.AttemptApi;
import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SaveStatsRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.server.handlers.AttemptHandler;
import javax.ws.rs.Path;

public class AttemptApiController implements AttemptApi {

  private final AttemptHandler attemptHandler;

  public AttemptApiController(final AttemptHandler attemptHandler) {
    this.attemptHandler = attemptHandler;
  }


  @Override
  @Path("/v1/attempt/save_stats")
  public InternalOperationResult saveStats(SaveStatsRequestBody requestBody) {
    return ConfigurationApi.execute(() -> attemptHandler.saveStats(requestBody));
  }

  @Override
  @Path("/v1/attempt/set_workflow_in_attempt")
  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody requestBody) {
    return ConfigurationApi.execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

}
