/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.Optional;

/**
 * Interface that indicates that an object exposes information used to identify an Airbyte stream.
 */
public interface AirbyteStreamAware {

  /**
   * Returns the {@link AirbyteStreamNameNamespacePair} identifying the Airbyte stream associated with
   * the object.
   *
   * @return The {@link AirbyteStreamNameNamespacePair} identifying the Airbyte stream (may be empty).
   */
  default Optional<AirbyteStreamNameNamespacePair> getAirbyteStream() {
    return Optional.empty();
  }

}
