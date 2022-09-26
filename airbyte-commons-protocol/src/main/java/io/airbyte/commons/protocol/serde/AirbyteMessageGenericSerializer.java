/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class AirbyteMessageGenericSerializer<T> implements AirbyteMessageSerializer<T> {

  private final AirbyteVersion version;

  @Override
  public String serialize(T message) {
    return Jsons.serialize(message);
  }

  @Override
  public AirbyteVersion getTargetVersion() {
    return version;
  }

}
