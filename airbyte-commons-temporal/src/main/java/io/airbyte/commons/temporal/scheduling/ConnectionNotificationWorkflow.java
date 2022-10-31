/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.io.IOException;

@WorkflowInterface
public interface ConnectionNotificationWorkflow {

  @WorkflowMethod
  void sendSchemaChangeNotification() throws IOException, InterruptedException;

}
