package io.airbyte.workers.temporal.scheduling.activities;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.nio.file.Path;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface PersistenceActivities {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class AttemptInput {

    private Path workspaceRoot;
    private long jobId;
    private int attempt;

  }

  @ActivityMethod
  void persistAttempt(AttemptInput input);
}
