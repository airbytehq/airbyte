/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.config.storage.CloudStorageConfigs;

/**
 * Describes logging configuration. For now it just contains configuration around storage medium,
 * but in the future will have other configuration options (e.g. json logging, etc).
 */
public class LogConfigs {

  public final static LogConfigs EMPTY = new LogConfigs(null);

  private final CloudStorageConfigs storageConfigs;

  public LogConfigs(final CloudStorageConfigs storageConfigs) {
    this.storageConfigs = storageConfigs;
  }

  public CloudStorageConfigs getStorageConfigs() {
    return storageConfigs;
  }

}
