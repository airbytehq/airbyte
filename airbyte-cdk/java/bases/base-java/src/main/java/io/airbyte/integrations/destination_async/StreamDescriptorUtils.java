/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashSet;
import java.util.Set;

/**
 * Helper functions to extract {@link StreamDescriptor} from other POJOs.
 */
public class StreamDescriptorUtils {

  public static StreamDescriptor fromRecordMessage(final AirbyteRecordMessage msg) {
    return new StreamDescriptor().withName(msg.getStream()).withNamespace(msg.getNamespace());
  }

  public static StreamDescriptor fromAirbyteStream(final AirbyteStream stream) {
    return new StreamDescriptor().withName(stream.getName()).withNamespace(stream.getNamespace());
  }

  public static StreamDescriptor fromConfiguredAirbyteSteam(final ConfiguredAirbyteStream stream) {
    return fromAirbyteStream(stream.getStream());
  }

  public static Set<StreamDescriptor> fromConfiguredCatalog(final ConfiguredAirbyteCatalog catalog) {
    final var pairs = new HashSet<StreamDescriptor>();

    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final var pair = fromAirbyteStream(stream.getStream());
      pairs.add(pair);
    }

    return pairs;
  }

}
