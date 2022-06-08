/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Adds secrets to a partial config based off a persistence.
 */
public class RealSecretsHydrator implements SecretsHydrator {

  private final ReadOnlySecretPersistence readOnlySecretPersistence;

  public RealSecretsHydrator(final ReadOnlySecretPersistence readOnlySecretPersistence) {
    this.readOnlySecretPersistence = readOnlySecretPersistence;
  }

  @Override
  public JsonNode hydrate(final JsonNode partialConfig) {
    return SecretsHelpers.combineConfig(partialConfig, readOnlySecretPersistence);
  }

  @Override
  public JsonNode hydrateSecretCoordinate(final JsonNode secretCoordinate) {
    return SecretsHelpers.hydrateSecretCoordinate(secretCoordinate, readOnlySecretPersistence);
  }

}
