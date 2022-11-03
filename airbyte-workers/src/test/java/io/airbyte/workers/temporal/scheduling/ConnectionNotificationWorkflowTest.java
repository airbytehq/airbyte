/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.temporal.scheduling.ConnectionNotificationWorkflow;
import io.airbyte.notification.NotificationClient;
import io.airbyte.workers.temporal.scheduling.activities.NotifySchemaChangeActivityImpl;
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
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@Slf4j

public class ConnectionNotificationWorkflowTest {

  private TestWorkflowEnvironment testEnv;
  private Worker notificationsWorker;
  private WorkflowClient client;
  private static final String NOTIFICATIONS_QUEUE = "NOTIFY";
  private ActivityOptions activityOptions;
  private TemporalProxyHelper temporalProxyHelper;

  private NotifySchemaChangeActivityImpl mNotifySchemaChangeActivity;

  @BeforeEach
  void setUp() throws IOException, InterruptedException {
    testEnv = TestWorkflowEnvironment.newInstance();
    notificationsWorker = testEnv.newWorker(NOTIFICATIONS_QUEUE);
    client = testEnv.getWorkflowClient();

    log.info("inside here");

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
    when(mNotifySchemaChangeActivity.notifySchemaChange(any(NotificationClient.class), any(UUID.class), any(boolean.class))).thenReturn(true);

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn("shortActivityOptions");
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);
    temporalProxyHelper = new TemporalProxyHelper(List.of(activityOptionsBeanRegistration));
    log.info("got here");

  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

  @Test
  void sendSchemaChangeNotificationNonBreakingChangeTest() throws IOException, InterruptedException {
    notificationsWorker.registerActivitiesImplementations(mNotifySchemaChangeActivity);
    testEnv.start();

    log.info("started test env");
    final ConnectionNotificationWorkflow workflow =
        client.newWorkflowStub(ConnectionNotificationWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(NOTIFICATIONS_QUEUE).build());

    log.info("created workflow");
    final UUID connectionId = UUID.randomUUID();
    final boolean isBreaking = false;

    workflow.sendSchemaChangeNotification(connectionId, isBreaking);

    log.info("sent schema change notif");

    verify(mNotifySchemaChangeActivity, times(1)).notifySchemaChange(any(NotificationClient.class), connectionId, isBreaking);
  }

}
