/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.transform_models;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the update of a field.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class UpdateFieldTransform {

  private final List<String> fieldName;
  private final JsonNode oldSchema;
  private final JsonNode newSchema;

  public List<String> getFieldName() {
    return new ArrayList<>(fieldName);
  }

  public JsonNode getOldSchema() {
    return oldSchema;
  }

  public JsonNode getNewSchema() {
    return newSchema;
  }

}
