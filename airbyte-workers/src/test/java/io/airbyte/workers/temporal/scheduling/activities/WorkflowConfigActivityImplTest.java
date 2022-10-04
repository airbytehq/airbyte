/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link WorkflowConfigActivityImpl} class.
 */
class WorkflowConfigActivityImplTest {

  @Test
  void testFetchingWorkflowRestartDelayInSeconds() {
    final Long workflowRestartDelaySeconds = 30L;
    final WorkflowConfigActivityImpl activity = new WorkflowConfigActivityImpl(workflowRestartDelaySeconds);
    Assertions.assertEquals(workflowRestartDelaySeconds, activity.getWorkflowRestartDelaySeconds().getSeconds());
  }

}
