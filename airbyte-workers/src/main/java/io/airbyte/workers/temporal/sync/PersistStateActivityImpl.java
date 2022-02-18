/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.nio.file.Path;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PersistStateActivityImpl implements PersistStateActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(PersistStateActivityImpl.class);
  private final Path workspaceRoot;
  private final ConfigRepository configRepository;

  public PersistStateActivityImpl(final Path workspaceRoot, final ConfigRepository configRepository) {
    this.workspaceRoot = workspaceRoot;
    this.configRepository = configRepository;
  }

  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput) {
    final State state = syncOutput.getState();
    if (state != null) {
      try {
        configRepository.updateConnectionState(connectionId, state);
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
      return true;
    } else {
      return false;
    }
  }

}
