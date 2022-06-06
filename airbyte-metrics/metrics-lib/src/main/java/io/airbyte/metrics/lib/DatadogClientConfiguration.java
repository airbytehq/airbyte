/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import io.airbyte.config.Configs;
import lombok.AllArgsConstructor;

/**
 * POJO of configuration required for publishing metrics.
 */
@AllArgsConstructor
public class DatadogClientConfiguration {

  public final String ddAgentHost;
  public final String ddPort;
  public final boolean publish;

  public DatadogClientConfiguration(final Configs configs) {
    this.ddAgentHost = configs.getDDAgentHost();
    this.ddPort = configs.getDDDogStatsDPort();
    this.publish = configs.getPublishMetrics();
  }

}
