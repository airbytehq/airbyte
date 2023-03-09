/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;
import static io.airbyte.commons.auth.AuthRoleConstants.OWNER;

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
import io.airbyte.commons.server.handlers.WorkspacesHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/workspaces")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class WorkspaceApiController implements WorkspaceApi {

  private final WorkspacesHandler workspacesHandler;

  public WorkspaceApiController(final WorkspacesHandler workspacesHandler) {
    this.workspacesHandler = workspacesHandler;
  }

  @Post("/create")
  @Secured({AUTHENTICATED_USER})
  @Override
  public WorkspaceRead createWorkspace(@Body final WorkspaceCreate workspaceCreate) {
    return ApiHelper.execute(() -> workspacesHandler.createWorkspace(workspaceCreate));
  }

  @Post("/delete")
  @Secured({OWNER})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void deleteWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    ApiHelper.execute(() -> {
      workspacesHandler.deleteWorkspace(workspaceIdRequestBody);
      return null;
    });
  }

  @Post("/get")
  @Secured({OWNER})
  @Override
  public WorkspaceRead getWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Post("/get_by_slug")
  @Secured({OWNER})
  @Override
  public WorkspaceRead getWorkspaceBySlug(@Body final SlugRequestBody slugRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Post("/list")
  @Secured({AUTHENTICATED_USER})
  @Override
  public WorkspaceReadList listWorkspaces() {
    return ApiHelper.execute(workspacesHandler::listWorkspaces);
  }

  @Post("/update")
  @Secured({OWNER})
  @Override
  public WorkspaceRead updateWorkspace(@Body final WorkspaceUpdate workspaceUpdate) {
    return ApiHelper.execute(() -> workspacesHandler.updateWorkspace(workspaceUpdate));
  }

  @Post("/tag_feedback_status_as_done")
  @Secured({OWNER})
  @Override
  public void updateWorkspaceFeedback(@Body final WorkspaceGiveFeedback workspaceGiveFeedback) {
    ApiHelper.execute(() -> {
      workspacesHandler.setFeedbackDone(workspaceGiveFeedback);
      return null;
    });
  }

  @Post("/update_name")
  @Secured({OWNER})
  @Override
  public WorkspaceRead updateWorkspaceName(@Body final WorkspaceUpdateName workspaceUpdateName) {
    return ApiHelper.execute(() -> workspacesHandler.updateWorkspaceName(workspaceUpdateName));
  }

  @Post("/get_by_connection_id")
  @Secured({AUTHENTICATED_USER})
  @Override
  public WorkspaceRead getWorkspaceByConnectionId(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> workspacesHandler.getWorkspaceByConnectionId(connectionIdRequestBody));
  }

}
