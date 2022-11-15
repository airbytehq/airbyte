/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.NotificationsApi;
import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;
import io.airbyte.server.handlers.WorkspacesHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/notifications/try")
@AllArgsConstructor
public class NotificationsApiController implements NotificationsApi {

  private final WorkspacesHandler workspacesHandler;

  @Override
  public NotificationRead tryNotificationConfig(final Notification notification) {
    return ConfigurationApi.execute(() -> workspacesHandler.tryNotification(notification));
  }

}
