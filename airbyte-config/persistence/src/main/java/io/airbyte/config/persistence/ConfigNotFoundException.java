/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import io.airbyte.config.AirbyteConfig;
import java.util.UUID;

public class ConfigNotFoundException extends Exception {

  private final String type;
  private final String configId;

  public ConfigNotFoundException(String type, String configId) {
    super(String.format("config type: %s id: %s", type, configId));
    this.type = type;
    this.configId = configId;
  }

  public ConfigNotFoundException(AirbyteConfig type, String configId) {
    this(type.toString(), configId);
  }

  public ConfigNotFoundException(AirbyteConfig type, UUID uuid) {
    this(type.toString(), uuid.toString());
  }

  public String getType() {
    return type;
  }

  public String getConfigId() {
    return configId;
  }

}
