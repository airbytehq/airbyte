/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.AttemptApi;
import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SaveStatsRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.server.handlers.AttemptHandler;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/api/v1/attempt/")
public class AttemptApiController implements AttemptApi {

  private final AttemptHandler attemptHandler;

  public AttemptApiController(final AttemptHandler attemptHandler) {
    this.attemptHandler = attemptHandler;
  }

  @Override
  @Post(uri = "/save_stats",
        processes = MediaType.APPLICATION_JSON)
  public InternalOperationResult saveStats(final SaveStatsRequestBody requestBody) {
    return ApiHelper.execute(() -> attemptHandler.saveStats(requestBody));
  }

  @Override
  @Post(uri = "/set_workflow_in_attempt",
        processes = MediaType.APPLICATION_JSON)
  public InternalOperationResult setWorkflowInAttempt(@Body final SetWorkflowInAttemptRequestBody requestBody) {
    return ApiHelper.execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

}
