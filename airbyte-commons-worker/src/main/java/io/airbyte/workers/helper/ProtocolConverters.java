/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.api.model.generated.StreamDescriptor;

/**
 * Utilities that convert protocol types into API or client representations of the protocol type.
 */
public class ProtocolConverters {

  public static StreamDescriptor streamDescriptorToApi(final io.airbyte.protocol.models.StreamDescriptor protocolStreamDescriptor) {
    return new StreamDescriptor().name(protocolStreamDescriptor.getName()).namespace(protocolStreamDescriptor.getNamespace());
  }

  public static io.airbyte.api.client.model.generated.StreamDescriptor streamDescriptorToClient(final io.airbyte.protocol.models.StreamDescriptor protocolStreamDescriptor) {
    return new io.airbyte.api.client.model.generated.StreamDescriptor()
        .name(protocolStreamDescriptor.getName())
        .namespace(protocolStreamDescriptor.getNamespace());
  }

  public static io.airbyte.protocol.models.StreamDescriptor streamDescriptorToProtocol(final StreamDescriptor apiStreamDescriptor) {
    return new io.airbyte.protocol.models.StreamDescriptor().withName(apiStreamDescriptor.getName())
        .withNamespace(apiStreamDescriptor.getNamespace());
  }

  public static io.airbyte.protocol.models.StreamDescriptor clientStreamDescriptorToProtocol(final io.airbyte.api.client.model.generated.StreamDescriptor clientStreamDescriptor) {
    return new io.airbyte.protocol.models.StreamDescriptor().withName(clientStreamDescriptor.getName())
        .withNamespace(clientStreamDescriptor.getNamespace());
  }

}
