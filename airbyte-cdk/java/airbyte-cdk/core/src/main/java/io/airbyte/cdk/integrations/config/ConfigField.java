/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.config;

abstract class ConfigField<CONFIG_TYPE extends AirbyteConfig, FIELD_TYPE> {

  protected final String fieldName;

  protected ConfigField(String fieldName) {
    this.fieldName = fieldName;
  }

  abstract FIELD_TYPE convert(CONFIG_TYPE config);

}
