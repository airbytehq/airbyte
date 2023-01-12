/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v0.transform_models;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the addition of a field to an {@link io.airbyte.protocol.models.v0.AirbyteStream}.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class AddFieldTransform {

  private final JsonNode schema;

  public JsonNode getSchema() {
    return schema;
  }

}
