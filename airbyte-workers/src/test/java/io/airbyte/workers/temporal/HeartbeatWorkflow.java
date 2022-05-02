/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

    private static final Logger LOGGER = LoggerFactory.getLogger(HeartbeatActivityImpl.class);

    private final Runnable runnable;

    public HeartbeatActivityImpl(Runnable runnable) {
      this.runnable = runnable;
    }

    @Override
    public void heartbeat() {
      runnable.run();
    }

  }

}
