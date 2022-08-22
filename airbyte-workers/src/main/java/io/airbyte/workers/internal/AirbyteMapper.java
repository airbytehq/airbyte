/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

/**
 * Interface to allow map operations on data as they pass from Source to Destination. This interface
 * will be updated in Protocol V2.
 */
public interface AirbyteMapper {

  ConfiguredAirbyteCatalog mapCatalog(ConfiguredAirbyteCatalog catalog);

  AirbyteMessage mapMessage(AirbyteMessage message);

}
