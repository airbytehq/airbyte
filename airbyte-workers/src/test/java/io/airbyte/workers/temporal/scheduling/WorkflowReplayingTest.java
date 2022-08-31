/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.workers.temporal.TemporalProxyHelper;
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

  private ActivityOptions activityOptions;
  private TemporalProxyHelper temporalProxyHelper;

  @BeforeEach
  void setUp() {
    activityOptions = ActivityOptions.newBuilder()
        .setHeartbeatTimeout(Duration.ofSeconds(30))
        .setStartToCloseTimeout(Duration.ofSeconds(120))
        .setRetryOptions(RetryOptions.newBuilder()
            .setMaximumAttempts(5)
            .setInitialInterval(Duration.ofSeconds(30))
            .setMaximumInterval(Duration.ofSeconds(600))
            .build())
        .build();

    final BeanIdentifier beanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration beanRegistration = mock(BeanRegistration.class);
    when(beanIdentifier.getName()).thenReturn("shortActivityOptions");
    when(beanRegistration.getIdentifier()).thenReturn(beanIdentifier);
    when(beanRegistration.getBean()).thenReturn(activityOptions);
    temporalProxyHelper = new TemporalProxyHelper(List.of(beanRegistration));
  }

  @Test
  void replaySimpleSuccessfulWorkflow() throws Exception {
    // This test ensures that a new version of the workflow doesn't break an in-progress execution
    // This JSON file is exported from Temporal directly (e.g.
    // `http://${temporal-ui}/namespaces/default/workflows/connection_manager_-${uuid}/${uuid}/history`)
    // and export
    final URL historyPath = getClass().getClassLoader().getResource("workflowHistory.json");

    final File historyFile = new File(historyPath.toURI());

    WorkflowReplayer.replayWorkflowExecution(historyFile, temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
  }

}
