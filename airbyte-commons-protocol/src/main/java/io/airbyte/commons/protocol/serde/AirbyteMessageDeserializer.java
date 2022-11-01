/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.version.Version;

public interface AirbyteMessageDeserializer<T> {

  T deserialize(final JsonNode json);

  Version getTargetVersion();

}
