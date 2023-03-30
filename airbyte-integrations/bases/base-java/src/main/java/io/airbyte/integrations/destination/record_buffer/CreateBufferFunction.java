/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

@FunctionalInterface
public interface CreateBufferFunction extends
    CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> {

  @Override
  SerializableBuffer apply(AirbyteStreamNameNamespacePair streamName, ConfiguredAirbyteCatalog configuredCatalog)
      throws Exception;

}
