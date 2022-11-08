/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.config.storage.CloudStorageConfigs;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.util.Optional;

/**
 * Describes logging configuration. For now it just contains configuration around storage medium,
 * but in the future will have other configuration options (e.g. json logging, etc).
 */
@Singleton
public class LogConfigs {

  public final static LogConfigs EMPTY = new LogConfigs(Optional.empty());

  private final CloudStorageConfigs storageConfigs;

  public LogConfigs(@Named("logStorageConfigs") final Optional<CloudStorageConfigs> storageConfigs) {
    this.storageConfigs = storageConfigs.orElse(null);
  }

  public CloudStorageConfigs getStorageConfigs() {
    return storageConfigs;
  }

}
