/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import io.airbyte.commons.version.Version;

public interface AirbyteMessageSerializer<T> {

  String serialize(final T message);

  Version getTargetVersion();

}
