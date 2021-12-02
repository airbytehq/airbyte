/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.WorkerUtils;
import java.io.IOException;
import java.nio.file.Path;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class PersistenceActivitiesImpl implements PersistenceActivities {

  private JobPersistence persistence;
  private WorkerEnvironment workerEnvironment;
  private LogConfigs logConfigs;

  @Override
  public void persistAttempt(final AttemptInput input) {
    try {
      final Path jobRoot = WorkerUtils.getJobRoot(input.getWorkspaceRoot(), String.valueOf(input.getJobId()), input.getAttempt());
      final Path logFilePath = jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
      final long persistedAttemptId = persistence.createAttempt(input.getJobId(), logFilePath);
      if (input.getAttempt() != persistedAttemptId) {
        throw new IllegalStateException();
      }
      // assertSameIds(attemptNumber, persistedAttemptId);
      LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, jobRoot);
    } catch (final IOException e) {
      e.printStackTrace();
    }
  }

}
