/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.NotificationsApiController;
import io.airbyte.server.handlers.WorkspacesHandler;
import org.glassfish.hk2.api.Factory;

public class NotificationsApiFactory implements Factory<NotificationsApiController> {

  private static WorkspacesHandler workspacesHandler;

  public static void setValues(final WorkspacesHandler workspacesHandler) {
    NotificationsApiFactory.workspacesHandler = workspacesHandler;
  }

  @Override
  public NotificationsApiController provide() {
    return new NotificationsApiController(NotificationsApiFactory.workspacesHandler);
  }

  @Override
  public void dispose(final NotificationsApiController instance) {
    /* no op */
  }

}
