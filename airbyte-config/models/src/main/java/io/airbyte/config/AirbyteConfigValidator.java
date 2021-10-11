/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.validation.json.AbstractSchemaValidator;
import java.nio.file.Path;

public class AirbyteConfigValidator extends AbstractSchemaValidator<ConfigSchema> {

  @Override
  public Path getSchemaPath(ConfigSchema configType) {
    return configType.getConfigSchemaFile().toPath();
  }

}
