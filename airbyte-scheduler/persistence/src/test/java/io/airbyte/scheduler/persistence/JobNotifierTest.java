/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.notification.NotificationClient;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class JobNotifierTest {

  private static final String WEBAPP_URL = "http://localhost:8000";
  private ConfigRepository configRepository;
  private JobNotifier jobNotifier;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    jobNotifier = new JobNotifier(WEBAPP_URL, configRepository);
  }

  @Test
  void testSendTestNotifications() throws IOException, InterruptedException {
    final StandardWorkspace workspace = getWorkspace();
    final JobNotifier notifier = spy(new JobNotifier(WEBAPP_URL, configRepository));
    final NotificationClient notificationClient = mock(NotificationClient.class);

    when(notificationClient.notify(anyString())).thenReturn(true);
    when(notifier.getNotificationClient(workspace.getNotifications().get(0))).thenReturn(notificationClient);

    assertTrue(notifier.sendTestNotifications(workspace));

    final ArgumentCaptor<String> message = ArgumentCaptor.forClass(String.class);
    verify(notificationClient).notify(message.capture());
    assertEquals(JobNotifier.NOTIFICATION_TEST_MESSAGE, message.getValue());
  }

  private static StandardWorkspace getWorkspace() {
    return new StandardWorkspace()
        .withCustomerId(UUID.randomUUID())
        .withNotifications(List.of(new Notification()
            .withNotificationType(NotificationType.SLACK)
            .withSlackConfiguration(new SlackNotificationConfiguration()
                .withWebhook("http://random.webhook.url"))));
  }

}
