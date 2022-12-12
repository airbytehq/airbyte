/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.WorkspaceApi;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.SlugRequestBody;
import io.airbyte.api.model.generated.WorkspaceCreate;
import io.airbyte.api.model.generated.WorkspaceGiveFeedback;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceReadList;
import io.airbyte.api.model.generated.WorkspaceUpdate;
import io.airbyte.api.model.generated.WorkspaceUpdateName;
import io.airbyte.server.handlers.WorkspacesHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/workspaces")
@AllArgsConstructor
public class WorkspaceApiController implements WorkspaceApi {

  private final WorkspacesHandler workspacesHandler;

  @Override
  public WorkspaceRead createWorkspace(final WorkspaceCreate workspaceCreate) {
    return ApiHelper.execute(() -> workspacesHandler.createWorkspace(workspaceCreate));
  }

  @Override
  public void deleteWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    ApiHelper.execute(() -> {
      workspacesHandler.deleteWorkspace(workspaceIdRequestBody);
      return null;
    });
  }

  @Override
  public WorkspaceRead getWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Override
  public WorkspaceRead getWorkspaceBySlug(final SlugRequestBody slugRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Override
  public WorkspaceReadList listWorkspaces() {
    return ApiHelper.execute(workspacesHandler::listWorkspaces);
  }

  @Override
  public WorkspaceRead updateWorkspace(final WorkspaceUpdate workspaceUpdate) {
    return ApiHelper.execute(() -> workspacesHandler.updateWorkspace(workspaceUpdate));
  }

  @Override
  public void updateWorkspaceFeedback(final WorkspaceGiveFeedback workspaceGiveFeedback) {
    ApiHelper.execute(() -> {
      workspacesHandler.setFeedbackDone(workspaceGiveFeedback);
      return null;
    });
  }

  @Override
  public WorkspaceRead updateWorkspaceName(final WorkspaceUpdateName workspaceUpdateName) {
    return ApiHelper.execute(() -> workspacesHandler.updateWorkspaceName(workspaceUpdateName));
  }

  @Override
  public WorkspaceRead getWorkspaceByConnectionId(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspaceByConnectionId(connectionIdRequestBody));
  }

}
