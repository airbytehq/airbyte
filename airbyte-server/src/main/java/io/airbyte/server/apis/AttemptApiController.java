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
import javax.transaction.Transactional;

@Controller("/api/v1/attempt/")
@Transactional
public class AttemptApiController implements AttemptApi {

  private final AttemptHandler attemptHandler;

  public AttemptApiController(final AttemptHandler attemptHandler) {
    this.attemptHandler = attemptHandler;
  }

  @Override
  @Post(uri = "/save_stats",
        processes = MediaType.APPLICATION_JSON)
  @Transactional
  public InternalOperationResult saveStats(final SaveStatsRequestBody saveStatsRequestBody) {
    throw new UnsupportedOperationException();
  }

  @Override
  @Post(uri = "/set_workflow_in_attempt",
        processes = MediaType.APPLICATION_JSON)
  @Transactional
  public InternalOperationResult setWorkflowInAttempt(@Body final SetWorkflowInAttemptRequestBody requestBody) {
    return ApiHelper.execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

}
