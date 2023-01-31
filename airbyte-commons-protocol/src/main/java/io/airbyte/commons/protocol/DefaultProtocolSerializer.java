/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class DefaultProtocolSerializer implements ProtocolSerializer {

  @Override
  public String serialize(ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
    return Jsons.serialize(configuredAirbyteCatalog);
  }

}
