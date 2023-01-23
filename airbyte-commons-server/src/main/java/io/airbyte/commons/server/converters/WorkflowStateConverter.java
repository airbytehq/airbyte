/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import io.airbyte.api.model.generated.WorkflowStateRead;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import jakarta.inject.Singleton;

@Singleton
public class WorkflowStateConverter {

  public WorkflowStateRead getWorkflowStateRead(final WorkflowState workflowState) {
    return new WorkflowStateRead().running(workflowState.isRunning());
  }

}
