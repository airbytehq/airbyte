/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;

/**
 * Data class that provides a way to store the output of a {@link SecretsHelpers} "split" operation
 * which takes a "full config" (including secrets) and creates a "partial config" (secrets removed
 * and has coordinate pointers to a persistence layer).
 *
 * The split methods don't actually update the persistence layer itself. The coordinate to secret
 * payload map in this class allows the system calling "split" to update the persistence with those
 * new coordinate values.
 */
public class SplitSecretConfig {

  private final JsonNode partialConfig;
  private final Map<SecretCoordinate, String> coordinateToPayload;

  public SplitSecretConfig(final JsonNode partialConfig, final Map<SecretCoordinate, String> coordinateToPayload) {
    this.partialConfig = partialConfig;
    this.coordinateToPayload = coordinateToPayload;
  }

  public JsonNode getPartialConfig() {
    return partialConfig;
  }

  public Map<SecretCoordinate, String> getCoordinateToPayload() {
    return coordinateToPayload;
  }

}
