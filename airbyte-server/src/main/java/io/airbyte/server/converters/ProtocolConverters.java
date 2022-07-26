/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.generated.StreamDescriptor;

/**
 * Utilities that convert protocol types into API representations of the protocol type.
 */
public class ProtocolConverters {

  public static StreamDescriptor streamDescriptorToApi(final io.airbyte.protocol.models.StreamDescriptor protocolStreamDescriptor) {
    return new StreamDescriptor().name(protocolStreamDescriptor.getName()).namespace(protocolStreamDescriptor.getNamespace());
  }

}
