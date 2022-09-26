/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;

public class AirbyteMessageGenericDeserializer<T> implements AirbyteMessageDeserializer<T> {

  final AirbyteVersion version;
  final Class<T> typeClass;

  public AirbyteMessageGenericDeserializer(final AirbyteVersion version, final Class<T> typeClass) {
    this.version = version;
    this.typeClass = typeClass;
  }

  @Override
  public T deserialize(String json) {
    return Jsons.deserialize(json, typeClass);
  }

  @Override
  public AirbyteVersion getTargetVersion() {
    return version;
  }

}
