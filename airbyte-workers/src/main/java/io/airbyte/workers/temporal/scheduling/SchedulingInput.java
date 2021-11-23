package io.airbyte.workers.temporal.scheduling;

import java.time.Duration;
import lombok.Value;

@Value
public class SchedulingInput {

  private final Duration schedulingPeriod;
}
