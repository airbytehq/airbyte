/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;

import io.airbyte.api.generated.SourceDefinitionSpecificationApi;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionSpecificationRead;
import io.airbyte.commons.server.handlers.SchedulerHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/source_definition_specifications")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class SourceDefinitionSpecificationApiController implements SourceDefinitionSpecificationApi {

  private final SchedulerHandler schedulerHandler;

  public SourceDefinitionSpecificationApiController(final SchedulerHandler schedulerHandler) {
    this.schedulerHandler = schedulerHandler;
  }

  @Post("/get")
  @Secured({AUTHENTICATED_USER})
  @Override
  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdWithWorkspaceId));
  }

}
