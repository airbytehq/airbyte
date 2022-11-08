/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.commons.temporal.scheduling.TaskQueueMapper;
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

  public RouterService(final ConfigRepository configRepository, final TaskQueueMapper taskQueueMapper) {
    this.configRepository = configRepository;
    this.taskQueueMapper = taskQueueMapper;
  }

  /**
   * Given a connectionId, look up the connection's configured {@link Geography} in the config DB and
   * use it to determine which Task Queue should be used for this connection's sync.
   */
  public String getTaskQueue(final UUID connectionId) throws IOException {
    final Geography geography = configRepository.getGeographyForConnection(connectionId);
    return taskQueueMapper.getTaskQueue(geography);
  }

}
