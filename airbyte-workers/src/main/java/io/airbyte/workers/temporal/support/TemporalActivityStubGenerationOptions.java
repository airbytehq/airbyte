/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import io.temporal.activity.ActivityOptions;
import java.util.Optional;
import lombok.AllArgsConstructor;

/**
 * Represents options that are used to generate a Temporal activity stub.
 */
@AllArgsConstructor
public class TemporalActivityStubGenerationOptions {

  /**
   * The Temporal {@link ActivityOptions} associated with the activity stub.
   */
  private ActivityOptions activityOptions;

  /**
   * The Temporal activity stub type.
   */
  private Class<?> activityStubClass;

  /**
   * The method arguments provided to the Temporal workflow method that uses the activity stub.
   *
   * These are optional and are provided in the event that the generation function needs them to
   * generate the activity stub.
   */
  private Object[] methodArguments;

  /**
   * The Temporal workflow version change ID.
   *
   * This is optional and is used by generator functions that need to query the workflow version in
   * order to determine how to generate the activity stub.
   */
  private String workflowVersionChangeId;

  public ActivityOptions getActivityOptions() {
    return activityOptions;
  }

  public Class<?> getActivityStubClass() {
    return activityStubClass;
  }

  public Optional<Object[]> getMethodArguments() {
    return Optional.ofNullable(methodArguments);
  }

  public Optional<String> getWorkflowVersionChangeId() {
    return Optional.ofNullable(workflowVersionChangeId);
  }

}
