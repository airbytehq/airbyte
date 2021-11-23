/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import java.time.Duration;
import lombok.Value;

@Value
public class SchedulingInput {

  private final Duration schedulingPeriod;

}
