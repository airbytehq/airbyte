/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Adds secrets to a partial config based off a persistence.
 */
public class RealSecretsHydrator implements SecretsHydrator {

  private final ReadOnlySecretPersistence readOnlySecretPersistence;

  public RealSecretsHydrator(ReadOnlySecretPersistence readOnlySecretPersistence) {
    this.readOnlySecretPersistence = readOnlySecretPersistence;
  }

  @Override
  public JsonNode hydrate(JsonNode partialConfig) {
    return SecretsHelpers.combineConfig(partialConfig, readOnlySecretPersistence);
  }

}
