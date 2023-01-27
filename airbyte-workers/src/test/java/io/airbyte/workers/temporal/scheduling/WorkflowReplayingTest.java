/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.workers.temporal.support.TemporalProxyHelper;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.testing.WorkflowReplayer;
import java.io.File;
import java.net.URL;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

// TODO: Auto generation of the input and more scenario coverage
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class WorkflowReplayingTest {

  private TemporalProxyHelper temporalProxyHelper;

  @BeforeEach
  void setUp() {
    ActivityOptions activityOptions = ActivityOptions.newBuilder()
        .setHeartbeatTimeout(Duration.ofSeconds(30))
        .setStartToCloseTimeout(Duration.ofSeconds(120))
        .setRetryOptions(RetryOptions.newBuilder()
            .setMaximumAttempts(5)
            .setInitialInterval(Duration.ofSeconds(30))
            .setMaximumInterval(Duration.ofSeconds(600))
            .build())
        .build();

    final BeanRegistration shortActivityOptionsBeanRegistration = getActivityOptionBeanRegistration("shortActivityOptions", activityOptions);
    final BeanRegistration longActivityOptionsBeanRegistration = getActivityOptionBeanRegistration("longRunActivityOptions", activityOptions);
    final BeanRegistration discoveryActivityOptionsBeanRegistration = getActivityOptionBeanRegistration("discoveryActivityOptions", activityOptions);

    temporalProxyHelper = new TemporalProxyHelper(
        List.of(shortActivityOptionsBeanRegistration, longActivityOptionsBeanRegistration, discoveryActivityOptionsBeanRegistration));
  }

  @Test
  void replaySimpleSuccessfulConnectionManagerWorkflow() throws Exception {
    // This test ensures that a new version of the workflow doesn't break an in-progress execution
    // This JSON file is exported from Temporal directly (e.g.
    // `http://${temporal-ui}/namespaces/default/workflows/connection_manager_-${uuid}/${uuid}/history`)
    // and export
    final URL historyPath = getClass().getClassLoader().getResource("connectionManagerWorkflowHistory.json");

    final File historyFile = new File(historyPath.toURI());

    WorkflowReplayer.replayWorkflowExecution(historyFile, temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
  }

  @Test
  void replaySyncWorkflowWithNormalization() throws Exception {
    // This test ensures that a new version of the workflow doesn't break an in-progress execution
    // This JSON file is exported from Temporal directly (e.g.
    // `http://${temporal-ui}/namespaces/default/workflows/connection_manager_-${uuid}/${uuid}/history`)
    // and export

    final URL historyPath = getClass().getClassLoader().getResource("syncWorkflowHistory.json");

    final File historyFile = new File(historyPath.toURI());

    WorkflowReplayer.replayWorkflowExecution(historyFile, temporalProxyHelper.proxyWorkflowClass(SyncWorkflowImpl.class));
  }

  private BeanRegistration getActivityOptionBeanRegistration(String name, ActivityOptions activityOptions) {
    final BeanIdentifier activitiesBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activitiesBeanIdentifier.getName()).thenReturn(name);
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activitiesBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);

    return activityOptionsBeanRegistration;
  }

}
