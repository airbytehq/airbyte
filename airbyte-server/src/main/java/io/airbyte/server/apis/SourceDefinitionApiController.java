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
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/source_definitions")
@AllArgsConstructor
public class SourceDefinitionApiController implements SourceDefinitionApi {

  private final SourceDefinitionsHandler sourceDefinitionsHandler;

  @Override
  public SourceDefinitionRead createCustomSourceDefinition(final CustomSourceDefinitionCreate customSourceDefinitionCreate) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.createCustomSourceDefinition(customSourceDefinitionCreate));
  }

  @Override
  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    ApiHelper.execute(() -> {
      sourceDefinitionsHandler.deleteSourceDefinition(sourceDefinitionIdRequestBody);
      return null;
    });
  }

  @Override
  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody));
  }

  @Override
  public SourceDefinitionRead getSourceDefinitionForWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.getSourceDefinitionForWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Override
  public PrivateSourceDefinitionRead grantSourceDefinitionToWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.grantSourceDefinitionToWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Override
  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return ApiHelper.execute(sourceDefinitionsHandler::listLatestSourceDefinitions);
  }

  @Override
  public PrivateSourceDefinitionReadList listPrivateSourceDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.listPrivateSourceDefinitions(workspaceIdRequestBody));
  }

  @Override
  public SourceDefinitionReadList listSourceDefinitions() {
    return ApiHelper.execute(sourceDefinitionsHandler::listSourceDefinitions);
  }

  @Override
  public SourceDefinitionReadList listSourceDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.listSourceDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public void revokeSourceDefinitionFromWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    ApiHelper.execute(() -> {
      sourceDefinitionsHandler.revokeSourceDefinitionFromWorkspace(sourceDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Override
  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate) {
    return ApiHelper.execute(() -> sourceDefinitionsHandler.updateSourceDefinition(sourceDefinitionUpdate));
  }

}
