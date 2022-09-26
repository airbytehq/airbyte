/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.protocol.serde.AirbyteMessageDeserializer;
import io.airbyte.commons.protocol.serde.AirbyteMessageSerializer;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import javax.annotation.PostConstruct;
import javax.inject.Singleton;

/**
 * AirbyteProtocol Message Serializer/Deserializer provider
 *
 * This class is intended to help access the serializer/deserializer for a given version of the
 * Airbyte Protocol.
 */
@Singleton
public class AirbyteSerDeProvider {

  private final List<AirbyteMessageDeserializer<?>> deserializersToRegister;
  private final List<AirbyteMessageSerializer<?>> serializersToRegister;

  private final Map<String, AirbyteMessageDeserializer<?>> deserializers = new HashMap<>();
  private final Map<String, AirbyteMessageSerializer<?>> serializers = new HashMap<>();

  public AirbyteSerDeProvider(final List<AirbyteMessageDeserializer<?>> deserializers,
                              final List<AirbyteMessageSerializer<?>> serializers) {
    deserializersToRegister = deserializers;
    serializersToRegister = serializers;
  }

  public AirbyteSerDeProvider() {
    this(Collections.emptyList(), Collections.emptyList());
  }

  @PostConstruct
  public void initialize() {
    deserializersToRegister.forEach(this::registerDeserializer);
    serializersToRegister.forEach(this::registerSerializer);
  }

  /**
   * Returns the Deserializer for the version if known else empty
   */
  public Optional<AirbyteMessageDeserializer<?>> getDeserializer(final AirbyteVersion version) {
    return Optional.ofNullable(deserializers.get(version.getMajorVersion()));
  }

  /**
   * Returns the Serializer for the version if known else empty
   */
  public Optional<AirbyteMessageSerializer<?>> getSerializer(final AirbyteVersion version) {
    return Optional.ofNullable(serializers.get(version.getMajorVersion()));
  }

  @VisibleForTesting
  void registerDeserializer(final AirbyteMessageDeserializer<?> deserializer) {
    final String key = deserializer.getTargetVersion().getMajorVersion();
    if (!deserializers.containsKey(key)) {
      deserializers.put(key, deserializer);
    } else {
      throw new RuntimeException(String.format("Trying to register a deserializer for protocol version {} when {} already exists",
          deserializer.getTargetVersion().serialize(), deserializers.get(key).getTargetVersion().serialize()));
    }
  }

  @VisibleForTesting
  void registerSerializer(final AirbyteMessageSerializer<?> serializer) {
    final String key = serializer.getTargetVersion().getMajorVersion();
    if (!serializers.containsKey(key)) {
      serializers.put(key, serializer);
    } else {
      throw new RuntimeException(String.format("Trying to register a serializer for protocol version {} when {} already exists",
          serializer.getTargetVersion().serialize(), serializers.get(key).getTargetVersion().serialize()));
    }
  }

  /**
   * returns the list of deserializer keys, mostly for test purpose
   */
  public Set<String> getDeserializerKeys() {
    return deserializers.keySet();
  }

  /**
   * returns the list of serializer keys, mostly for test purpose
   */
  public Set<String> getSerializerKeys() {
    return serializers.keySet();
  }

}
