/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.NotificationsApi;
import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;
import io.airbyte.server.handlers.WorkspacesHandler;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/api/v1/notifications/try")
public class NotificationsApiController implements NotificationsApi {

  private final WorkspacesHandler workspacesHandler;

  public NotificationsApiController(final WorkspacesHandler workspacesHandler) {
    this.workspacesHandler = workspacesHandler;
  }

  @Post
  @Override
  public NotificationRead tryNotificationConfig(@Body final Notification notification) {
    return ApiHelper.execute(() -> workspacesHandler.tryNotification(notification));
  }

}
