/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Adds secrets to a partial config.
 */
public interface SecretsHydrator {

  /**
   * Adds secrets to a partial config.
   *
   * @param partialConfig partial config (without secrets)
   * @return full config with secrets
   */
  JsonNode hydrate(JsonNode partialConfig);

}
