/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.OpenapiApi;
import io.airbyte.server.handlers.OpenApiConfigHandler;
import java.io.File;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/openapi")
@AllArgsConstructor
public class OpenapiApiController implements OpenapiApi {

  private final OpenApiConfigHandler openApiConfigHandler;

  @Override
  public File getOpenApiSpec() {
    return ConfigurationApi.execute(openApiConfigHandler::getFile);
  }

}
