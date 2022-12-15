/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.SourceDefinitionSpecificationApi;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionSpecificationRead;
import io.airbyte.server.handlers.SchedulerHandler;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import javax.transaction.Transactional;

@Controller("/api/v1/source_definition_specifications")
@Transactional
public class SourceDefinitionSpecificationApiController implements SourceDefinitionSpecificationApi {

  private final SchedulerHandler schedulerHandler;

  public SourceDefinitionSpecificationApiController(final SchedulerHandler schedulerHandler) {
    this.schedulerHandler = schedulerHandler;
  }

  @Post("/get")
  @Override
  @Transactional
  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdWithWorkspaceId));
  }

}
