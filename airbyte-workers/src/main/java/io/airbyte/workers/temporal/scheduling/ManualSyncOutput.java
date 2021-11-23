package io.airbyte.workers.temporal.scheduling;

import lombok.Value;

@Value
public class ManualSyncOutput {

  private final boolean submitted;
}
