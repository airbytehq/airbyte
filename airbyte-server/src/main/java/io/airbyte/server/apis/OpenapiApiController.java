/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.OpenapiApi;
import io.airbyte.server.handlers.OpenApiConfigHandler;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import java.io.File;
import javax.transaction.Transactional;

@Controller("/api/v1/openapi")
@Transactional
public class OpenapiApiController implements OpenapiApi {

  private final OpenApiConfigHandler openApiConfigHandler;

  public OpenapiApiController(final OpenApiConfigHandler openApiConfigHandler) {
    this.openApiConfigHandler = openApiConfigHandler;
  }

  @Get(produces = "text/plain")
  @Override
  @Transactional
  public File getOpenApiSpec() {
    return ApiHelper.execute(openApiConfigHandler::getFile);
  }

}
