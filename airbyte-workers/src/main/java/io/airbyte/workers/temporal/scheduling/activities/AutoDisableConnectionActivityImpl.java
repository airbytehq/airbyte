/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Sets;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Set;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class AutoDisableConnectionActivityImpl implements AutoDisableConnectionActivity {

  @VisibleForTesting
  public static final Set<ConfigType> AUTO_DISABLE_CONFIG_TYPES = Sets.newHashSet(ConfigType.SYNC, ConfigType.RESET_CONNECTION);

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private FeatureFlags featureFlags;
  private Configs configs;

  @Override
  public void autoDisableFailingConnection(final AutoDisableConnectionActivityInput input) {
    if (featureFlags.autoDisablesFailingConnections()) {
      try {
        final List<JobStatus> jobStatuses = jobPersistence.listJobStatusWithConnection(input.getConnectionId(), AUTO_DISABLE_CONFIG_TYPES,
            input.getCurrTimestamp().minus(configs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable(), ChronoUnit.DAYS));

        if (jobStatuses.size() == 0)
          return;

        boolean shouldDisable = true;
        int numFailures = 0;

        // jobs are sorted from most recent to least recent
        for (final JobStatus jobStatus : jobStatuses) {
          if (jobStatus == JobStatus.FAILED) {
            numFailures++;
            if (numFailures == configs.getMaxFailedJobsInARowBeforeConnectionDisable())
              break;
          } else if (jobStatus == JobStatus.SUCCEEDED) {
            shouldDisable = false;
            break;
          }
        }

        if (shouldDisable) {
          final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());
          standardSync.setStatus(Status.INACTIVE);
          configRepository.writeStandardSync(standardSync);
        }
      } catch (final Exception e) {
        throw new RetryableException(e);
      }
    }
  }

}
