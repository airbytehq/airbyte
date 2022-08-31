/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import io.temporal.activity.ActivityOptions;
import java.util.Optional;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class TemporalActivityStubGenerationOptions {

  private ActivityOptions activityOptions;

  private Class<?> activityStubClass;

  private Object[] methodArguments;

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
