/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

  /**
   * Takes in the secret coordinate in form of a JSON and fetches the secret from the store
   *
   * @param secretCoordinate The co-ordinate of the secret in the store in JSON format
   * @return original secret value
   */
  JsonNode hydrateSecretCoordinate(final JsonNode secretCoordinate);

}
