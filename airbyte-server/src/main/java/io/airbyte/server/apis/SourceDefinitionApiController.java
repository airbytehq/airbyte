/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.ADMIN;
import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;
import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

import io.airbyte.api.generated.SourceDefinitionApi;
import io.airbyte.api.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.model.generated.PrivateSourceDefinitionRead;
import io.airbyte.api.model.generated.PrivateSourceDefinitionReadList;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionRead;
import io.airbyte.api.model.generated.SourceDefinitionReadList;
import io.airbyte.api.model.generated.SourceDefinitionUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.server.handlers.SourceDefinitionsHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/source_definitions")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Context
@Secured(SecurityRule.IS_AUTHENTICATED)
public class SourceDefinitionApiController implements SourceDefinitionApi {

  private final SourceDefinitionsHandler sourceDefinitionsHandler;

  public SourceDefinitionApiController(final SourceDefinitionsHandler sourceDefinitionsHandler) {
    this.sourceDefinitionsHandler = sourceDefinitionsHandler;
  }

  @Post("/create_custom")
  @Secured({EDITOR})
  @Override
  public SourceDefinitionRead createCustomSourceDefinition(final CustomSourceDefinitionCreate customSourceDefinitionCreate) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.createCustomSourceDefinition(customSourceDefinitionCreate));
  }

  @Post("/delete")
  @Secured({ADMIN})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    ApiHelper.execute(() -> {
      sourceDefinitionsHandler.deleteSourceDefinition(sourceDefinitionIdRequestBody);
      return null;
    });
  }

  @Post("/get")
  @Secured({AUTHENTICATED_USER})
  @Override
  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody));
  }

  @Post("/get_for_workspace")
  @Secured({READER})
  @Override
  public SourceDefinitionRead getSourceDefinitionForWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.getSourceDefinitionForWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Post("/grant_definition")
  @Secured({ADMIN})
  @Override
  public PrivateSourceDefinitionRead grantSourceDefinitionToWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.grantSourceDefinitionToWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Post("/list_latest")
  @Secured({AUTHENTICATED_USER})
  @Override
  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return ApiHelper.execute(sourceDefinitionsHandler::listLatestSourceDefinitions);
  }

  @Post("/list_private")
  @Secured({ADMIN})
  @Override
  public PrivateSourceDefinitionReadList listPrivateSourceDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.listPrivateSourceDefinitions(workspaceIdRequestBody));
  }

  @Post("/list")
  @Secured({AUTHENTICATED_USER})
  @Override
  public SourceDefinitionReadList listSourceDefinitions() {
    return ApiHelper.execute(sourceDefinitionsHandler::listSourceDefinitions);
  }

  @Post("/list_for_workspace")
  @Secured({READER})
  @Override
  public SourceDefinitionReadList listSourceDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.listSourceDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Post("/revoke_definition")
  @Secured({ADMIN})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void revokeSourceDefinitionFromWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    ApiHelper.execute(() -> {
      sourceDefinitionsHandler.revokeSourceDefinitionFromWorkspace(sourceDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Post("/update")
  @Secured({AUTHENTICATED_USER})
  @Override
  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.updateSourceDefinition(sourceDefinitionUpdate));
  }

}
