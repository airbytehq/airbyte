/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Optional;

/**
 * No-op hydrator. Used if there is no secrets persistence configured for this Airbyte instance.
 */
public class NoOpSecretsHydrator implements SecretsHydrator {

  @Override
  public JsonNode hydrate(final JsonNode partialConfig) {
    return partialConfig;
  }

  @Override
  public Optional<String> read(SecretCoordinate secretCoordinate) {
    throw new RuntimeException("read is not allowed in NoOpSecretHydrator");
  }

  @Override
  public boolean isReadAllowed() {
    return false;
  }

}
