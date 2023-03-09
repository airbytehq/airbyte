/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;

import io.airbyte.api.generated.NotificationsApi;
import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;
import io.airbyte.commons.server.handlers.WorkspacesHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/notifications/try")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class NotificationsApiController implements NotificationsApi {

  private final WorkspacesHandler workspacesHandler;

  public NotificationsApiController(final WorkspacesHandler workspacesHandler) {
    this.workspacesHandler = workspacesHandler;
  }

  @Post
  @Secured({AUTHENTICATED_USER})
  @Override
  public NotificationRead tryNotificationConfig(@Body final Notification notification) {
    return ApiHelper.execute(() -> workspacesHandler.tryNotification(notification));
  }

}
