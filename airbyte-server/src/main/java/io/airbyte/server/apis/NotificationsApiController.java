package io.airbyte.server.apis;

import io.airbyte.api.generated.NotificationsApi;
import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;

public class NotificationsApiController implements NotificationsApi {

  @Override public NotificationRead tryNotificationConfig(final Notification notification) {
    return ConfigurationApi.execute(() -> workspacesHandler.tryNotification(notification));
  }
}
