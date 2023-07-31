/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStream;

/**
 * Collection of utility methods used to convert objects to {@link AirbyteStreamNameNamespacePair}
 * objects.
 */
public class AirbyteStreamUtils {

  /**
   * Converts an {@link AirbyteStream} to a {@link AirbyteStreamNameNamespacePair}.
   *
   * @param airbyteStream The {@link AirbyteStream} to convert.
   * @return The {@link AirbyteStreamNameNamespacePair}.
   */
  public static AirbyteStreamNameNamespacePair convertFromAirbyteStream(final AirbyteStream airbyteStream) {
    return new AirbyteStreamNameNamespacePair(airbyteStream.getName(), airbyteStream.getNamespace());
  }

  /**
   * Converts a stream name and namespace into a {@link AirbyteStreamNameNamespacePair}.
   *
   * @param name The name of the stream.
   * @param namespace The namespace of the stream.
   * @return The {@link AirbyteStreamNameNamespacePair}.
   */
  public static AirbyteStreamNameNamespacePair convertFromNameAndNamespace(final String name, final String namespace) {
    return new AirbyteStreamNameNamespacePair(name, namespace);
  }

}
