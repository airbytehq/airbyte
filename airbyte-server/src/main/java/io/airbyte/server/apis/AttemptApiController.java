/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SaveStatsRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.server.handlers.AttemptHandler;
import io.micronaut.http.annotation.Controller;
import lombok.extern.slf4j.Slf4j;

@Controller("/v1/attempt/")
@Slf4j
public class AttemptApiController {

  private final AttemptHandler attemptHandler;

  public AttemptApiController(final AttemptHandler attemptHandler) {
    this.attemptHandler = attemptHandler;
  }

  /*
   * @Post(uri = "/save_stats", produces = MediaType.APPLICATION_JSON, consumes =
   * MediaType.APPLICATION_JSON)
   */
  public InternalOperationResult saveStats(final SaveStatsRequestBody saveStatsRequestBody) {
    log.error("Tessssttttttttt");

    throw new UnsupportedOperationException();
  }

  /*
   * @Post(uri = "/set_workflow_in_attempt", produces = MediaType.APPLICATION_JSON, consumes =
   * MediaType.APPLICATION_JSON)
   */
  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody requestBody) {
    log.error("Tessssttttttttt 22");

    return ApiHelper.execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

}
