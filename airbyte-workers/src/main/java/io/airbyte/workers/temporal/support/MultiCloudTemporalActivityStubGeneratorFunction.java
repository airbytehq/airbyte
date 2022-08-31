/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.workers.temporal.sync.RouterService;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
@Named("multiCloudTemporalActivityStubGeneratorFunction")
public class MultiCloudTemporalActivityStubGeneratorFunction implements TemporalActivityStubGeneratorFunction {

  public static final int CURRENT_VERSION = 2;
  public static final int PREV_VERSION = 1;

  /**
   * {@link RouterService} used to determine which task queue to use for other activities.
   */
  @Inject
  private RouterService routerService;

  @Override
  public Object apply(final TemporalActivityStubGenerationOptions options) {
    final int version = Workflow.getVersion(options.getWorkflowVersionChangeId().orElse(null), Workflow.DEFAULT_VERSION, CURRENT_VERSION);
    final String taskQueue = routerService.getTaskQueue(getConnectionId(options.getMethodArguments()));

    /**
     * The current version calls a new activity to determine which Task Queue to use for other
     * activities. The previous version doesn't call this new activity, and instead lets each activity
     * inherit the workflow's Task Queue.
     */
    if (version > PREV_VERSION) {
      return Workflow.newActivityStub(options.getActivityStubClass(), setTaskQueue(options.getActivityOptions(), taskQueue));
    } else {
      return Workflow.newActivityStub(options.getActivityStubClass(), options.getActivityOptions());
    }
  }

  private ActivityOptions setTaskQueue(final ActivityOptions activityOptions, final String taskQueue) {
    return ActivityOptions.newBuilder(activityOptions).setTaskQueue(taskQueue).build();
  }

  private UUID getConnectionId(final Optional methodArguments) {
    if (methodArguments.isPresent()) {
      final Object[] arguments = (Object[]) methodArguments.get();
      return (UUID) Arrays.stream(arguments).filter(a -> a.getClass().equals(UUID.class)).findFirst().get();
    } else {
      return null;
    }
  }

  @VisibleForTesting
  public void setRouterService(final RouterService routerService) {
    this.routerService = routerService;
  }

}
