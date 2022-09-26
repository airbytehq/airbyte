/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.stubs;

import io.airbyte.commons.temporal.TemporalUtils;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.time.Duration;

@WorkflowInterface
public interface HeartbeatWorkflow {

  @WorkflowMethod
  void execute();

  class HeartbeatWorkflowImpl implements HeartbeatWorkflow {

    private final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofDays(1))
        .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();

    private final HeartbeatActivity heartbeatActivity = Workflow.newActivityStub(HeartbeatActivity.class, options);

    @Override
    public void execute() {
      heartbeatActivity.heartbeat();
    }

  }

  @ActivityInterface
  interface HeartbeatActivity {

    @ActivityMethod
    void heartbeat();

  }

  class HeartbeatActivityImpl implements HeartbeatActivity {

    private final Runnable runnable;

    public HeartbeatActivityImpl(final Runnable runnable) {
      this.runnable = runnable;
    }

    @Override
    public void heartbeat() {
      runnable.run();
    }

  }

}
