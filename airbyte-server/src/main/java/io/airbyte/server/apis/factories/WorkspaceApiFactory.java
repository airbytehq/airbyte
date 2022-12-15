/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.WorkspaceApiController;
import io.airbyte.server.handlers.WorkspacesHandler;
import org.glassfish.hk2.api.Factory;

public class WorkspaceApiFactory implements Factory<WorkspaceApiController> {

  private static WorkspacesHandler workspacesHandler;

  public static void setValues(final WorkspacesHandler workspacesHandler) {
    WorkspaceApiFactory.workspacesHandler = workspacesHandler;
  }

  @Override
  public WorkspaceApiController provide() {
    return new WorkspaceApiController(WorkspaceApiFactory.workspacesHandler);
  }

  @Override
  public void dispose(final WorkspaceApiController instance) {
    /* no op */
  }

}
