/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

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
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import javax.transaction.Transactional;

@Controller("/api/v1/source_definitions")
@Context
@Transactional
public class SourceDefinitionApiController implements SourceDefinitionApi {

  private final SourceDefinitionsHandler sourceDefinitionsHandler;

  public SourceDefinitionApiController(final SourceDefinitionsHandler sourceDefinitionsHandler) {
    this.sourceDefinitionsHandler = sourceDefinitionsHandler;
  }

  @Post("/create_custom")
  @Override
  @Transactional
  public SourceDefinitionRead createCustomSourceDefinition(final CustomSourceDefinitionCreate customSourceDefinitionCreate) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.createCustomSourceDefinition(customSourceDefinitionCreate));
  }

  @Post("/delete")
  @Override
  @Transactional
  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    ApiHelper.execute(() -> {
      sourceDefinitionsHandler.deleteSourceDefinition(sourceDefinitionIdRequestBody);
      return null;
    });
  }

  @Post("/get")
  @Override
  @Transactional
  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody));
  }

  @Post("/get_for_workspace")
  @Override
  @Transactional
  public SourceDefinitionRead getSourceDefinitionForWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.getSourceDefinitionForWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Post("/grant_definition")
  @Override
  @Transactional
  public PrivateSourceDefinitionRead grantSourceDefinitionToWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.grantSourceDefinitionToWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Post("/list_latest")
  @Override
  @Transactional
  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return ApiHelper.execute(sourceDefinitionsHandler::listLatestSourceDefinitions);
  }

  @Post("/list_private")
  @Override
  @Transactional
  public PrivateSourceDefinitionReadList listPrivateSourceDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.listPrivateSourceDefinitions(workspaceIdRequestBody));
  }

  @Post("/list")
  @Override
  @Transactional
  public SourceDefinitionReadList listSourceDefinitions() {
    return ApiHelper.execute(sourceDefinitionsHandler::listSourceDefinitions);
  }

  @Post("/list_for_workspace")
  @Override
  @Transactional
  public SourceDefinitionReadList listSourceDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.listSourceDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Post("/revoke_definition")
  @Override
  @Transactional
  public void revokeSourceDefinitionFromWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    ApiHelper.execute(() -> {
      sourceDefinitionsHandler.revokeSourceDefinitionFromWorkspace(sourceDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Post("/update")
  @Override
  @Transactional
  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.updateSourceDefinition(sourceDefinitionUpdate));
  }

}
