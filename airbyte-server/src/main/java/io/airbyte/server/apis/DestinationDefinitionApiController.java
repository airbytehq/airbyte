/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.DestinationDefinitionApi;
import io.airbyte.api.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionRead;
import io.airbyte.api.model.generated.DestinationDefinitionReadList;
import io.airbyte.api.model.generated.DestinationDefinitionUpdate;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionRead;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionReadList;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/destination_definitions")
@AllArgsConstructor
public class DestinationDefinitionApiController implements DestinationDefinitionApi {

  private final DestinationDefinitionsHandler destinationDefinitionsHandler;

  @Override
  public DestinationDefinitionRead createCustomDestinationDefinition(final CustomDestinationDefinitionCreate customDestinationDefinitionCreate) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.createCustomDestinationDefinition(customDestinationDefinitionCreate));
  }

  @Override
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    ApiHelper.execute(() -> {
      destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);
      return null;
    });
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Override
  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper
        .execute(() -> destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    return ApiHelper.execute(destinationDefinitionsHandler::listDestinationDefinitions);
  }

  @Override
  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.listDestinationDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return ApiHelper.execute(destinationDefinitionsHandler::listLatestDestinationDefinitions);
  }

  @Override
  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.listPrivateDestinationDefinitions(workspaceIdRequestBody));
  }

  @Override
  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    ApiHelper.execute(() -> {
      destinationDefinitionsHandler.revokeDestinationDefinitionFromWorkspace(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

}
