/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.workers.temporal.support.TemporalProxyHelper;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityOptions;
import io.temporal.testing.WorkflowReplayer;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class CheckConnectionWorkflowTest {

  private ActivityOptions activityOptions;
  private TemporalProxyHelper temporalProxyHelper;

  @BeforeEach
  void setUp() {
    activityOptions = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofMinutes(5))
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn("checkActivityOptions");
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);
    temporalProxyHelper = new TemporalProxyHelper(List.of(activityOptionsBeanRegistration));
  }

  @Test
  void replayOldWorkflow() throws Exception {
    // This test ensures that a new version of the workflow doesn't break an in-progress execution
    // This JSON file is exported from Temporal directly (e.g.
    // `http://${temporal-ui}/namespaces/default/workflows/${uuid}/${uuid}/history`) and export

    WorkflowReplayer.replayWorkflowExecutionFromResource("checkWorkflowHistory.json",
        temporalProxyHelper.proxyWorkflowClass(CheckConnectionWorkflowImpl.class));
  }

}
