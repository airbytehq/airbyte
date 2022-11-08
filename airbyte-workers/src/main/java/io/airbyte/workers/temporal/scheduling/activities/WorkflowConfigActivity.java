/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.time.Duration;

/**
 * Custom Temporal activity that can be used to retrieve configuration values managed by the
 * application framework from the application context.
 */
@ActivityInterface
public interface WorkflowConfigActivity {

  /**
   * Fetches the configured workflow restart delay in seconds from the application context.
   *
   * @return The workflow restart delay in seconds.
   */
  @ActivityMethod
  Duration getWorkflowRestartDelaySeconds();

}
