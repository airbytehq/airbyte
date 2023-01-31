/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class NotificationsApiTest extends BaseControllerTest {

  @Test
  void testTryNotificationConfig() {
    Mockito.when(workspacesHandler.tryNotification(Mockito.any()))
        .thenReturn(new NotificationRead());
    final String path = "/api/v1/notifications/try";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new Notification())),
        HttpStatus.OK);
  }

}
