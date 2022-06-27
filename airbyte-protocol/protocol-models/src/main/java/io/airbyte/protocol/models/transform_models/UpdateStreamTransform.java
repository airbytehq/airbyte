/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.transform_models;

import java.util.HashSet;
import java.util.Set;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the update of an {@link io.airbyte.protocol.models.AirbyteStream}.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class UpdateStreamTransform {

  private final Set<FieldTransform> fieldTransforms;

  public Set<FieldTransform> getFieldTransforms() {
    return new HashSet<>(fieldTransforms);
  }

}
