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
 * Represents the removal of a field to an {@link io.airbyte.protocol.models.AirbyteStream}.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class RemoveFieldTransform {

  private final List<String> fieldName;
  private final JsonNode schema;

  public List<String> getFieldName() {
    return new ArrayList<>(fieldName);
  }

  public JsonNode getSchema() {
    return schema;
  }

}
