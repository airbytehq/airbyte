/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v0.transform_models;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the update of a field.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class UpdateFieldSchemaTransform {

  private final JsonNode oldSchema;
  private final JsonNode newSchema;

  public JsonNode getOldSchema() {
    return oldSchema;
  }

  public JsonNode getNewSchema() {
    return newSchema;
  }

}
