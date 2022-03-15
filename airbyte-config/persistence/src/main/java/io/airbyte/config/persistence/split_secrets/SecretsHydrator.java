/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Optional;

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
  JsonNode hydrate(final JsonNode partialConfig);

  Optional<String> read(final SecretCoordinate secretCoordinate);

  boolean isReadAllowed();

}
