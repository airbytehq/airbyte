/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;

import io.airbyte.api.generated.DestinationDefinitionSpecificationApi;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionSpecificationRead;
import io.airbyte.commons.server.handlers.SchedulerHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/destination_definition_specifications")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class DestinationDefinitionSpecificationApiController implements DestinationDefinitionSpecificationApi {

  private final SchedulerHandler schedulerHandler;

  public DestinationDefinitionSpecificationApiController(final SchedulerHandler schedulerHandler) {
    this.schedulerHandler = schedulerHandler;
  }

  @Post("/get")
  @Secured({AUTHENTICATED_USER})
  @Override
  public DestinationDefinitionSpecificationRead getDestinationDefinitionSpecification(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> schedulerHandler.getDestinationSpecification(destinationDefinitionIdWithWorkspaceId));
  }

}
