/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.DestinationDefinitionSpecificationApi;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionSpecificationRead;
import io.airbyte.server.handlers.SchedulerHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/destination_definition_specifications/get")
@AllArgsConstructor
public class DestinationDefinitionSpecificationApiController implements DestinationDefinitionSpecificationApi {

  private final SchedulerHandler schedulerHandler;

  @Override
  public DestinationDefinitionSpecificationRead getDestinationDefinitionSpecification(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ConfigurationApi.execute(() -> schedulerHandler.getDestinationSpecification(destinationDefinitionIdWithWorkspaceId));
  }

}
