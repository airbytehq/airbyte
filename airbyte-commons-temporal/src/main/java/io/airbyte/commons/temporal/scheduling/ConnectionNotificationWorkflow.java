/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.io.IOException;
import java.util.UUID;

@WorkflowInterface
public interface ConnectionNotificationWorkflow {

  @WorkflowMethod
  void sendSchemaChangeNotification(UUID connectionId, boolean isBreaking) throws IOException, InterruptedException;

}
