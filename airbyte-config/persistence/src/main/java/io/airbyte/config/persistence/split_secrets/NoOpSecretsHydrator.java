/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * No-op hydrator. Used if there is no secrets persistence configured for this Airbyte instance.
 */
public class NoOpSecretsHydrator implements SecretsHydrator {

  @Override
  public JsonNode hydrate(JsonNode partialConfig) {
    return partialConfig;
  }

}
