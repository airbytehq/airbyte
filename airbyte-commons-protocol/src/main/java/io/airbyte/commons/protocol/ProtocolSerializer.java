/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public interface ProtocolSerializer {

  String serialize(final ConfiguredAirbyteCatalog configuredAirbyteCatalog);

}
