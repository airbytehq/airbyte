/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.workers.temporal.sync.RouterService;
import io.micronaut.core.util.StringUtils;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Named("multiCloudTemporalActivityStubGeneratorFunction")
@Slf4j
public class MultiCloudTemporalActivityStubGeneratorFunction implements TemporalActivityStubGeneratorFunction {

  static final int CURRENT_VERSION = 2;
  static final int PREV_VERSION = 1;

  /**
   * {@link RouterService} used to determine which task queue to use for other activities.
   */
  @Inject
  private RouterService routerService;

  @Override
  public Object apply(final TemporalActivityStubGenerationOptions options) {
    final int version = getWorkflowVersion(options.getWorkflowVersionChangeId().orElse(null));
    final UUID connectionId = getConnectionId(options.getMethodArguments());

    /**
     * The current version calls a new activity to determine which Task Queue to use for other
     * activities. The previous version doesn't call this new activity, and instead lets each activity
     * inherit the workflow's Task Queue.
     */
    if (version > PREV_VERSION) {
      final String taskQueue = routerService.getTaskQueue(connectionId);
      log.debug("Creating new activity stub '{}' to execute on task queue '{}'...", options.getActivityStubClass().getName(), taskQueue);
      return generateActivityStub(options.getActivityStubClass(), buildActivityOptionsWithTaskQueue(options.getActivityOptions(), taskQueue));
    } else {
      log.debug("Creating new activity stub '{}' to execute on default task queue...", options.getActivityStubClass().getName());
      return generateActivityStub(options.getActivityStubClass(), options.getActivityOptions());
    }
  }

  /**
   * Retrieves the current version for the Temporal workflow represented by the provided change ID
   * value.
   *
   * @param workflowVersionChangeId The Temporal workflow change ID.
   * @return The current version of the Temporal workflow or {@link Integer#MIN_VALUE} if a blank
   *         change ID value is provided.
   */
  @VisibleForTesting
  int getWorkflowVersion(final String workflowVersionChangeId) {
    if (StringUtils.isNotEmpty(workflowVersionChangeId)) {
      return Workflow.getVersion(workflowVersionChangeId, Workflow.DEFAULT_VERSION, CURRENT_VERSION);
    } else {
      return Integer.MIN_VALUE;
    }
  }

  /**
   * Generates the Temporal activity stub.
   *
   * @param activityStubClass The type of the Temporal activity stub.
   * @param activityOptions The Temporal {@link ActivityOptions}.
   * @return The Temporal activity stub.
   */
  @VisibleForTesting
  Object generateActivityStub(final Class<?> activityStubClass, final ActivityOptions activityOptions) {
    return Workflow.newActivityStub(activityStubClass, activityOptions);
  }

  /**
   * Builds a new {@link ActivityOptions} from the provided {@link ActivityOptions}. The new options
   * include the provided task queue.
   *
   * @param activityOptions The existing base {@link ActivityOptions}.
   * @param taskQueue The task queue for the executing the associated Temporal activity.
   * @return The new {@link ActivityOptions}.
   */
  private ActivityOptions buildActivityOptionsWithTaskQueue(final ActivityOptions activityOptions, final String taskQueue) {
    return ActivityOptions.newBuilder(activityOptions).setTaskQueue(taskQueue).build();
  }

  /**
   * Extracts the connection ID parameter from the provided method arguments, if present.
   *
   * @param methodArguments The array of arguments for the invoked Temporal workflow method associated
   *        with the activity.
   * @return The connection ID value or {@code null} if it is not present or cannot be found in the
   *         argument array.
   */
  private UUID getConnectionId(final Optional<Object[]> methodArguments) {
    if (methodArguments.isPresent()) {
      final Object[] arguments = methodArguments.get();
      return (UUID) Arrays.stream(arguments).filter(a -> a.getClass().equals(UUID.class)).findFirst().orElse(null);
    } else {
      return null;
    }
  }

  @VisibleForTesting
  public void setRouterService(final RouterService routerService) {
    this.routerService = routerService;
  }

}
