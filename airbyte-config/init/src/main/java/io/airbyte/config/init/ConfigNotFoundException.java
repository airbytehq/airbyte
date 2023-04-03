/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

public class ConfigNotFoundException extends Exception {

  private static final long serialVersionUID = 836273627;
  private final String type;
  private final String configId;

  public ConfigNotFoundException(final String type, final String configId) {
    super(String.format("config type: %s id: %s", type, configId));
    this.type = type;
    this.configId = configId;
  }

  public String getType() {
    return type;
  }

  public String getConfigId() {
    return configId;
  }

}
