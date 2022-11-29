/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SaveStatsRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.server.handlers.AttemptHandler;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;
import lombok.extern.slf4j.Slf4j;

@Controller("/v1/attempt/")
@Api(description = "the Attempt API")
@Slf4j
public class AttemptApiController {

  private final AttemptHandler attemptHandler;

  public AttemptApiController(final AttemptHandler attemptHandler) {
    this.attemptHandler = attemptHandler;
  }

  @Post(uri = "/save_stats",
        produces = MediaType.APPLICATION_JSON,
        consumes = MediaType.APPLICATION_JSON)
  @ApiOperation(value = "For worker to set sync stats of a running attempt.",
                notes = "",
                tags = {"attempt", "internal"})
  @ApiResponses(value = {
    @ApiResponse(code = 200,
                 message = "Successful Operation",
                 response = InternalOperationResult.class)})
  public InternalOperationResult saveStats(final SaveStatsRequestBody saveStatsRequestBody) {
    log.error("Tessssttttttttt");

    throw new UnsupportedOperationException();
  }

  @Post(uri = "/set_workflow_in_attempt",
        produces = MediaType.APPLICATION_JSON,
        consumes = MediaType.APPLICATION_JSON)
  @ApiOperation(value = "For worker to register the workflow id in attempt.",
                notes = "",
                tags = {"attempt", "internal"})
  @ApiResponses(value = {
    @ApiResponse(code = 200,
                 message = "Successful Operation",
                 response = InternalOperationResult.class)})
  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody requestBody) {
    return ApiHelper.execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

}
