/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.config.Geography;
import io.airbyte.config.persistence.ConfigRepository;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

/**
 * Decides which Task Queue should be used for a given connection's sync operations, based on the
 * configured {@link Geography}
 */
@Singleton
@Slf4j
public class RouterService {

  private final ConfigRepository configRepository;
  private final TaskQueueMapper taskQueueMapper;

  private final FeatureFlags featureFlags;

  public RouterService(final ConfigRepository configRepository,
                       final TaskQueueMapper taskQueueMapper,
                       final FeatureFlags featureFlags) {
    this.configRepository = configRepository;
    this.taskQueueMapper = taskQueueMapper;
    this.featureFlags = featureFlags;
  }

  /**
   * Given a connectionId, look up the connection's configured {@link Geography} in the config DB and
   * use it to determine which Task Queue should be used for this connection's sync.
   */
  public String getTaskQueue(final UUID connectionId, final TemporalJobType jobType) throws IOException {
    final Geography geography = configRepository.getGeographyForConnection(connectionId);
    return taskQueueMapper.getTaskQueue(geography, jobType);
  }

  // This function is only getting called for discover/check functions. Today (02.07) they are behind
  // feature flag
  // so even the geography might be in EU they will still be directed to US.
  public String getTaskQueueForWorkspace(final UUID workspaceId, final TemporalJobType jobType) throws IOException {
    if (featureFlags.routeTaskQueueForWorkspaceEnabled() || featureFlags.routeTaskQueueForWorkspaceAllowList().contains(workspaceId.toString())) {
      final Geography geography = configRepository.getGeographyForWorkspace(workspaceId);
      return taskQueueMapper.getTaskQueue(geography, jobType);
    } else {
      return taskQueueMapper.getTaskQueue(Geography.AUTO, jobType);
    }
  }

}
