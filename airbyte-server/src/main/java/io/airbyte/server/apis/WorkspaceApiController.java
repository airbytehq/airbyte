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
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import javax.transaction.Transactional;

@Controller("/api/v1/workspaces")
@Transactional
public class WorkspaceApiController implements WorkspaceApi {

  private final WorkspacesHandler workspacesHandler;

  public WorkspaceApiController(final WorkspacesHandler workspacesHandler) {
    this.workspacesHandler = workspacesHandler;
  }

  @Post("/create")
  @Override
  @Transactional
  public WorkspaceRead createWorkspace(@Body final WorkspaceCreate workspaceCreate) {
    return ApiHelper.execute(() -> workspacesHandler.createWorkspace(workspaceCreate));
  }

  @Post("/delete")
  @Override
  @Transactional
  public void deleteWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    ApiHelper.execute(() -> {
      workspacesHandler.deleteWorkspace(workspaceIdRequestBody);
      return null;
    });
  }

  @Post("/get")
  @Override
  @Transactional
  public WorkspaceRead getWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Post("/get_by_slug")
  @Override
  @Transactional
  public WorkspaceRead getWorkspaceBySlug(@Body final SlugRequestBody slugRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Post("/list")
  @Override
  @Transactional
  public WorkspaceReadList listWorkspaces() {
    return ApiHelper.execute(workspacesHandler::listWorkspaces);
  }

  @Post("/update")
  @Override
  @Transactional
  public WorkspaceRead updateWorkspace(@Body final WorkspaceUpdate workspaceUpdate) {
    return ApiHelper.execute(() -> workspacesHandler.updateWorkspace(workspaceUpdate));
  }

  @Post("/tag_feedback_status_as_done")
  @Override
  @Transactional
  public void updateWorkspaceFeedback(@Body final WorkspaceGiveFeedback workspaceGiveFeedback) {
    ApiHelper.execute(() -> {
      workspacesHandler.setFeedbackDone(workspaceGiveFeedback);
      return null;
    });
  }

  @Post("/update_name")
  @Override
  @Transactional
  public WorkspaceRead updateWorkspaceName(@Body final WorkspaceUpdateName workspaceUpdateName) {
    return ApiHelper.execute(() -> workspacesHandler.updateWorkspaceName(workspaceUpdateName));
  }

  @Post("/get_by_connection_id")
  @Override
  @Transactional
  public WorkspaceRead getWorkspaceByConnectionId(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspaceByConnectionId(connectionIdRequestBody));
  }

}
