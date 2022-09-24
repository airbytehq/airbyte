/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import io.airbyte.commons.protocol.serde.AirbyteMessageDeserializer;
import io.airbyte.commons.protocol.serde.AirbyteMessageSerializer;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class AirbyteSerDeProvider {

  private final Map<String, AirbyteMessageDeserializer<?>> deserializers = new HashMap<>();
  private final Map<String, AirbyteMessageSerializer<?>> serializers = new HashMap<>();

  public Optional<AirbyteMessageDeserializer<?>> getDeserializer(final AirbyteVersion version) {
    return Optional.ofNullable(deserializers.get(version.getMajorVersion()));
  }

  public Optional<AirbyteMessageSerializer<?>> getSerializer(final AirbyteVersion version) {
    return Optional.ofNullable(serializers.get(version.getMajorVersion()));
  }

  public void registerDeserializer(final AirbyteMessageDeserializer<?> deserializer) {
    final String key = deserializer.getTargetVersion().getMajorVersion();
    if (!deserializers.containsKey(key)) {
      deserializers.put(key, deserializer);
    } else {
      throw new RuntimeException(String.format("Trying to register a deserializer for protocol version {} when {} already exists",
          deserializer.getTargetVersion().serialize(), deserializers.get(key).getTargetVersion().serialize()));
    }
  }

  public void registerSerializer(final AirbyteMessageSerializer<?> serializer) {
    final String key = serializer.getTargetVersion().getMajorVersion();
    if (!serializers.containsKey(key)) {
      serializers.put(key, serializer);
    } else {
      throw new RuntimeException(String.format("Trying to register a serializer for protocol version {} when {} already exists",
          serializer.getTargetVersion().serialize(), serializers.get(key).getTargetVersion().serialize()));
    }
  }

}
