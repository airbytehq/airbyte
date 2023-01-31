/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public class AirbyteMessageGenericSerializer<T> implements AirbyteMessageSerializer<T> {

  @Getter
  private final Version targetVersion;

  @Override
  public String serialize(T message) {
    return Jsons.serialize(message);
  }

}
