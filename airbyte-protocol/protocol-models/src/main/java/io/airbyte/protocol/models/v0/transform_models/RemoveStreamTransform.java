/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v0.transform_models;

import io.airbyte.protocol.models.v0.StreamDescriptor;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the removal of an {@link io.airbyte.protocol.models.v0.AirbyteStream} to a
 * {@link io.airbyte.protocol.models.v0.AirbyteCatalog}.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class RemoveStreamTransform {

  private final StreamDescriptor streamDescriptor;

  public StreamDescriptor getStreamDescriptor() {
    return streamDescriptor;
  }

}
