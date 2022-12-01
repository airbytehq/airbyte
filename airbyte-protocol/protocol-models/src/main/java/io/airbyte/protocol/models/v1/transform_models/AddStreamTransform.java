/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v1.transform_models;

import io.airbyte.protocol.models.v1.StreamDescriptor;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the addition of an {@link io.airbyte.protocol.models.AirbyteStream} to a
 * {@link io.airbyte.protocol.models.AirbyteCatalog}.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public class AddStreamTransform {

  private final StreamDescriptor streamDescriptor;

  public StreamDescriptor getStreamDescriptor() {
    return streamDescriptor;
  }

}
