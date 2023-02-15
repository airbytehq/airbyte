/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.ADMIN;
import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;
import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

import io.airbyte.api.generated.ConnectorBuilderProjectApi;
import io.airbyte.api.generated.SourceDefinitionApi;
import io.airbyte.api.model.generated.ConnectorBuilderProjectIdWithWorkspaceId;
import io.airbyte.api.model.generated.ConnectorBuilderProjectWithWorkspaceId;
import io.airbyte.api.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.model.generated.ExistingConnectorBuilderProjectWithWorkspaceId;
import io.airbyte.api.model.generated.PrivateSourceDefinitionRead;
import io.airbyte.api.model.generated.PrivateSourceDefinitionReadList;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionRead;
import io.airbyte.api.model.generated.SourceDefinitionReadList;
import io.airbyte.api.model.generated.SourceDefinitionUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.auth.SecuredWorkspace;
import io.airbyte.commons.server.handlers.ConnectorBuilderProjectsHandler;
import io.airbyte.commons.server.handlers.SourceDefinitionsHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/connector_builder_projects")
@Context
@Secured(SecurityRule.IS_AUTHENTICATED)
public class ConnectorBuilderProjectApiController implements ConnectorBuilderProjectApi {

  private final ConnectorBuilderProjectsHandler connectorBuilderProjectsHandler;

  public ConnectorBuilderProjectApiController(final ConnectorBuilderProjectsHandler connectorBuilderProjectsHandler) {
    this.connectorBuilderProjectsHandler = connectorBuilderProjectsHandler;
  }

  @Override
  @Post(uri = "/create")
  @Status(HttpStatus.CREATED)
  @Secured({EDITOR})
  @SecuredWorkspace
  public ConnectorBuilderProjectIdWithWorkspaceId createProject(final ConnectorBuilderProjectWithWorkspaceId connectorBuilderProjectWithWorkspaceId) {
    return ApiHelper.execute(() -> connectorBuilderProjectsHandler.createConnectorBuilderProject(connectorBuilderProjectWithWorkspaceId));
  }

  @Override
  @Post(uri = "/delete")
  @Status(HttpStatus.NO_CONTENT)
  @Secured({EDITOR})
  @SecuredWorkspace
  public void deleteProject(final ConnectorBuilderProjectIdWithWorkspaceId connectorBuilderProjectIdWithWorkspaceId) {
    ApiHelper.execute(() -> { connectorBuilderProjectsHandler.deleteConnectorBuilderProject(connectorBuilderProjectIdWithWorkspaceId); return null; });
  }

  @Override
  @Post(uri = "/update")
  @Status(HttpStatus.NO_CONTENT)
  @Secured({EDITOR})
  @SecuredWorkspace
  public void updateProject(final ExistingConnectorBuilderProjectWithWorkspaceId existingConnectorBuilderProjectWithWorkspaceId) {
    ApiHelper.execute(() -> { connectorBuilderProjectsHandler.updateConnectorBuilderProject(existingConnectorBuilderProjectWithWorkspaceId); return null; });
  }
}
