/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.DestinationDefinitionApi;
import io.airbyte.api.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.model.generated.CustomDestinationDefinitionUpdate;
import io.airbyte.api.model.generated.DestinationDefinitionCreate;
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
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.createCustomDestinationDefinition(customDestinationDefinitionCreate));
  }

  // TODO: Deprecate this route in favor of createCustomDestinationDefinition
  // since all connector definitions created through the API are custom
  @Override
  public DestinationDefinitionRead createDestinationDefinition(final DestinationDefinitionCreate destinationDefinitionCreate) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.createPrivateDestinationDefinition(destinationDefinitionCreate));
  }

  @Override
  public void deleteCustomDestinationDefinition(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    ConfigurationApi.execute(() -> {
      destinationDefinitionsHandler.deleteCustomDestinationDefinition(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Override
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    ConfigurationApi.execute(() -> {
      destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);
      return null;
    });
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Override
  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ConfigurationApi
        .execute(() -> destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    return ConfigurationApi.execute(destinationDefinitionsHandler::listDestinationDefinitions);
  }

  @Override
  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.listDestinationDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return ConfigurationApi.execute(destinationDefinitionsHandler::listLatestDestinationDefinitions);
  }

  @Override
  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.listPrivateDestinationDefinitions(workspaceIdRequestBody));
  }

  @Override
  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    ConfigurationApi.execute(() -> {
      destinationDefinitionsHandler.revokeDestinationDefinitionFromWorkspace(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Override
  public DestinationDefinitionRead updateCustomDestinationDefinition(final CustomDestinationDefinitionUpdate customDestinationDefinitionUpdate) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.updateCustomDestinationDefinition(customDestinationDefinitionUpdate));
  }

  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return ConfigurationApi.execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

}
