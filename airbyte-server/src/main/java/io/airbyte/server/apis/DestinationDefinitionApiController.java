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
import io.micronaut.context.annotation.Context;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/api/v1/destination_definitions")
@Context
public class DestinationDefinitionApiController implements DestinationDefinitionApi {

  private final DestinationDefinitionsHandler destinationDefinitionsHandler;

  public DestinationDefinitionApiController(final DestinationDefinitionsHandler destinationDefinitionsHandler) {
    this.destinationDefinitionsHandler = destinationDefinitionsHandler;
  }

  @Post(uri = "/create_custom")
  @Override
  public DestinationDefinitionRead createCustomDestinationDefinition(final CustomDestinationDefinitionCreate customDestinationDefinitionCreate) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.createCustomDestinationDefinition(customDestinationDefinitionCreate));
  }

  @Post(uri = "/delete")
  @Override
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    ApiHelper.execute(() -> {
      destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);
      return null;
    });
  }

  @Post(uri = "/get")
  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Post(uri = "/get_for_workspace")
  @Override
  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Post(uri = "/grant_definition")
  @Override
  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper
        .execute(() -> destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Post(uri = "/list")
  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    return ApiHelper.execute(destinationDefinitionsHandler::listDestinationDefinitions);
  }

  @Post(uri = "/list_for_workspace")
  @Override
  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.listDestinationDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Post(uri = "/list_latest")
  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return ApiHelper.execute(destinationDefinitionsHandler::listLatestDestinationDefinitions);
  }

  @Post(uri = "/list_private")
  @Override
  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.listPrivateDestinationDefinitions(workspaceIdRequestBody));
  }

  @Post(uri = "/revoke_definition")
  @Override
  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    ApiHelper.execute(() -> {
      destinationDefinitionsHandler.revokeDestinationDefinitionFromWorkspace(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Post(uri = "/update")
  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

}
