/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.ADMIN;
import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;
import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

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
import io.airbyte.commons.server.handlers.DestinationDefinitionsHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/destination_definitions")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Context
@Secured(SecurityRule.IS_AUTHENTICATED)
public class DestinationDefinitionApiController implements DestinationDefinitionApi {

  private final DestinationDefinitionsHandler destinationDefinitionsHandler;

  public DestinationDefinitionApiController(final DestinationDefinitionsHandler destinationDefinitionsHandler) {
    this.destinationDefinitionsHandler = destinationDefinitionsHandler;
  }

  @Post(uri = "/create_custom")
  @Secured({EDITOR})
  @Override
  public DestinationDefinitionRead createCustomDestinationDefinition(final CustomDestinationDefinitionCreate customDestinationDefinitionCreate) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.createCustomDestinationDefinition(customDestinationDefinitionCreate));
  }

  @Post(uri = "/delete")
  @Secured({ADMIN})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    ApiHelper.execute(() -> {
      destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);
      return null;
    });
  }

  @Post(uri = "/get")
  @Secured({AUTHENTICATED_USER})
  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Post(uri = "/get_for_workspace")
  @Secured({READER})
  @Override
  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Post(uri = "/grant_definition")
  @Secured({ADMIN})
  @Override
  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return ApiHelper
        .execute(() -> destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Post(uri = "/list")
  @Secured({AUTHENTICATED_USER})
  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    return ApiHelper.execute(destinationDefinitionsHandler::listDestinationDefinitions);
  }

  @Post(uri = "/list_for_workspace")
  @Secured({READER})
  @Override
  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.listDestinationDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Post(uri = "/list_latest")
  @Secured({AUTHENTICATED_USER})
  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return ApiHelper.execute(destinationDefinitionsHandler::listLatestDestinationDefinitions);
  }

  @Post(uri = "/list_private")
  @Secured({ADMIN})
  @Override
  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.listPrivateDestinationDefinitions(workspaceIdRequestBody));
  }

  @Post(uri = "/revoke_definition")
  @Secured({ADMIN})
  @Override
  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    ApiHelper.execute(() -> {
      destinationDefinitionsHandler.revokeDestinationDefinitionFromWorkspace(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Post(uri = "/update")
  @Secured({AUTHENTICATED_USER})
  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return ApiHelper.execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

}
