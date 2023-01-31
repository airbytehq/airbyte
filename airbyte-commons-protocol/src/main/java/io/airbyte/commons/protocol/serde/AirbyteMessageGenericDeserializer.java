/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import lombok.Getter;

public class AirbyteMessageGenericDeserializer<T> implements AirbyteMessageDeserializer<T> {

  @Getter
  final Version targetVersion;
  final Class<T> typeClass;

  public AirbyteMessageGenericDeserializer(final Version targetVersion, final Class<T> typeClass) {
    this.targetVersion = targetVersion;
    this.typeClass = typeClass;
  }

  @Override
  public T deserialize(JsonNode json) {
    return Jsons.object(json, typeClass);
  }

}
