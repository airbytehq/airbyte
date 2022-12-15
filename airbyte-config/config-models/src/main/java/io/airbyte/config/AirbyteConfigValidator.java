/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.validation.json.AbstractSchemaValidator;
import java.nio.file.Path;

public class AirbyteConfigValidator extends AbstractSchemaValidator<ConfigSchema> {

  final public static AirbyteConfigValidator AIRBYTE_CONFIG_VALIDATOR = new AirbyteConfigValidator();

  @Override
  public Path getSchemaPath(final ConfigSchema configType) {
    return configType.getConfigSchemaFile().toPath();
  }

}
