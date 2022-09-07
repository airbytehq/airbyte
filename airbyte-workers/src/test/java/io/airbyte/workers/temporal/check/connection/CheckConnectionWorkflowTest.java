/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.temporal.testing.WorkflowReplayer;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class CheckConnectionWorkflowTest {

  @Test
  void replayOldWorkflow() throws Exception {
    // This test ensures that a new version of the workflow doesn't break an in-progress execution
    // This JSON file is exported from Temporal directly (e.g.
    // `http://${temporal-ui}/namespaces/default/workflows/${uuid}/${uuid}/history`) and export

    WorkflowReplayer.replayWorkflowExecutionFromResource("checkWorkflowHistory.json", CheckConnectionWorkflowImpl.class);
  }

}
