/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.stubs;

import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;

@SuppressWarnings("PMD.UnusedPrivateField")
public class InvalidTestWorkflowImpl implements TestWorkflow {

  @TemporalActivityStub(activityOptionsBeanName = "missingActivityOptions")
  private TestActivity testActivity;

  @Override
  public void run() throws RetryableException {}

  @Override
  public void cancel() {}

  @Override
  public Integer getState() {
    return 1;
  }

}
