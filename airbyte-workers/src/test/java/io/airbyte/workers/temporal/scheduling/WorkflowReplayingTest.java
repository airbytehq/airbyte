/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.temporal.testing.WorkflowReplayer;
import java.io.File;
import java.net.URL;
import org.junit.jupiter.api.Test;

// TODO: Auto generation of the input and more scenario coverage
public class WorkflowReplayingTest {

  @Test
  public void replaySimpleSuccessfulWorkflow() throws Exception {
    final URL historyPath = getClass().getClassLoader().getResource("workflowHistory.json");

    final File historyFile = new File(historyPath.toURI());

    WorkflowReplayer.replayWorkflowExecution(historyFile, ConnectionManagerWorkflowImpl.class);
  }

}
