/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.transform_models;

import io.airbyte.protocol.models.StreamDescriptor;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the diff between two {@link io.airbyte.protocol.models.AirbyteStream}.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public final class StreamTransform {

  private final StreamTransformType transformType;
  private final StreamDescriptor streamDescriptor;
  private final UpdateStreamTransform updateStreamTransform;

  public static StreamTransform createAddStreamTransform(final StreamDescriptor streamDescriptor) {
    return new StreamTransform(StreamTransformType.ADD_STREAM, streamDescriptor, null);
  }

  public static StreamTransform createRemoveStreamTransform(final StreamDescriptor streamDescriptor) {
    return new StreamTransform(StreamTransformType.REMOVE_STREAM, streamDescriptor, null);
  }

  public static StreamTransform createUpdateStreamTransform(final StreamDescriptor streamDescriptor,
                                                            final UpdateStreamTransform updateStreamTransform) {
    return new StreamTransform(StreamTransformType.UPDATE_STREAM, streamDescriptor, updateStreamTransform);
  }

  public StreamTransformType getTransformType() {
    return transformType;
  }

  public StreamDescriptor getStreamDescriptor() {
    return streamDescriptor;
  }

  public UpdateStreamTransform getUpdateStreamTransform() {
    return updateStreamTransform;
  }

}
