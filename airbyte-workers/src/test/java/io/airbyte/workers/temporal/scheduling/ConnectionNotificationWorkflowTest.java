/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.commons.temporal.scheduling.ConnectionNotificationWorkflow;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.notification.SlackNotificationClient;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.NotifySchemaChangeActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.SlackConfigActivityImpl;
import io.airbyte.workers.temporal.support.TemporalProxyHelper;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityOptions;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.common.RetryOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.io.IOException;
import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectionNotificationWorkflowTest {

  private TestWorkflowEnvironment testEnv;
  private Worker notificationsWorker;
  private WorkflowClient client;
  private static final String NOTIFICATIONS_QUEUE = "NOTIFY";
  private ActivityOptions activityOptions;
  private TemporalProxyHelper temporalProxyHelper;

  private NotifySchemaChangeActivityImpl mNotifySchemaChangeActivity;
  private SlackConfigActivityImpl mSlackConfigActivity;
  private ConfigFetchActivityImpl mConfigFetchActivity;

  @BeforeEach
  void setUp() throws IOException, InterruptedException, ApiException, JsonValidationException, ConfigNotFoundException {
    testEnv = TestWorkflowEnvironment.newInstance();
    notificationsWorker = testEnv.newWorker(NOTIFICATIONS_QUEUE);
    client = testEnv.getWorkflowClient();

    activityOptions = ActivityOptions.newBuilder()
        .setHeartbeatTimeout(Duration.ofSeconds(30))
        .setStartToCloseTimeout(Duration.ofSeconds(120))
        .setRetryOptions(RetryOptions.newBuilder()
            .setMaximumAttempts(5)
            .setInitialInterval(Duration.ofSeconds(30))
            .setMaximumInterval(Duration.ofSeconds(600))
            .build())
        .build();

    mNotifySchemaChangeActivity = mock(NotifySchemaChangeActivityImpl.class);
    when(mNotifySchemaChangeActivity.notifySchemaChange(any(SlackNotificationClient.class), any(UUID.class), any(boolean.class))).thenReturn(true);

    mSlackConfigActivity = mock(SlackConfigActivityImpl.class);
    when(mSlackConfigActivity.fetchSlackConfiguration(any(UUID.class))).thenReturn(
        Optional.ofNullable(new SlackNotificationConfiguration().withWebhook("webhook")));

    mConfigFetchActivity = mock(ConfigFetchActivityImpl.class);

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn("shortActivityOptions");
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);
    temporalProxyHelper = new TemporalProxyHelper(List.of(activityOptionsBeanRegistration));

    notificationsWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(ConnectionNotificationWorkflowImpl.class));
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

  @Test
  void sendSchemaChangeNotificationNonBreakingChangeTest()
      throws IOException, InterruptedException, ApiException, JsonValidationException, ConfigNotFoundException {
    notificationsWorker.registerActivitiesImplementations(mNotifySchemaChangeActivity, mSlackConfigActivity, mConfigFetchActivity);
    testEnv.start();

    final ConnectionNotificationWorkflow workflow =
        client.newWorkflowStub(ConnectionNotificationWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(NOTIFICATIONS_QUEUE).build());

    final UUID connectionId = UUID.randomUUID();

    when(mConfigFetchActivity.getBreakingChange(connectionId)).thenReturn(Optional.of(false));
    workflow.sendSchemaChangeNotification(connectionId);

    verify(mNotifySchemaChangeActivity, times(1)).notifySchemaChange(any(SlackNotificationClient.class), any(UUID.class), any(boolean.class));
  }

}
