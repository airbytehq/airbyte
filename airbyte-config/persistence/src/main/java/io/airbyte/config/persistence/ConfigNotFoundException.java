/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import io.airbyte.config.AirbyteConfig;
import java.util.UUID;

public class ConfigNotFoundException extends Exception {

  private static final long serialVersionUID = 836273627;
  private final String type;
  private final String configId;

  public ConfigNotFoundException(final String type, final String configId) {
    super(String.format("config type: %s id: %s", type, configId));
    this.type = type;
    this.configId = configId;
  }

  public ConfigNotFoundException(final AirbyteConfig type, final String configId) {
    this(type.toString(), configId);
  }

  public ConfigNotFoundException(final AirbyteConfig type, final UUID uuid) {
    this(type.toString(), uuid.toString());
  }

  public String getType() {
    return type;
  }

  public String getConfigId() {
    return configId;
  }

}
