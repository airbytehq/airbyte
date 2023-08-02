/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

public interface BufferCreateFunction extends
    CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> {

  @Override
  SerializableBuffer apply(AirbyteStreamNameNamespacePair stream, ConfiguredAirbyteCatalog configuredCatalog)
      throws Exception;

}
