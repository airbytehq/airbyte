/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.protocol.serde.AirbyteMessageDeserializer;
import io.airbyte.commons.protocol.serde.AirbyteMessageSerializer;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AirbyteSerDeProviderTest {

  AirbyteSerDeProvider serDeProvider;
  AirbyteMessageDeserializer<String> deserV0;
  AirbyteMessageDeserializer<String> deserV1;

  AirbyteMessageSerializer<String> serV0;
  AirbyteMessageSerializer<String> serV1;

  @BeforeEach
  void beforeEach() {
    serDeProvider = new AirbyteSerDeProvider();

    deserV0 = buildDeserializer(new AirbyteVersion("0.1.0"));
    deserV1 = buildDeserializer(new AirbyteVersion("1.1.0"));
    serDeProvider.registerDeserializer(deserV0);
    serDeProvider.registerDeserializer(deserV1);

    serV0 = buildSerializer(new AirbyteVersion("0.2.0"));
    serV1 = buildSerializer(new AirbyteVersion("1.0.0"));
    serDeProvider.registerSerializer(serV0);
    serDeProvider.registerSerializer(serV1);
  }

  @Test
  void testGetDeserializer() {
    assertEquals(Optional.of(deserV0), serDeProvider.getDeserializer(new AirbyteVersion("0.1.0")));
    assertEquals(Optional.of(deserV0), serDeProvider.getDeserializer(new AirbyteVersion("0.2.0")));
    assertEquals(Optional.of(deserV1), serDeProvider.getDeserializer(new AirbyteVersion("1.1.0")));
    assertEquals(Optional.empty(), serDeProvider.getDeserializer(new AirbyteVersion("2.0.0")));
  }

  @Test
  void testGetSerializer() {
    assertEquals(Optional.of(serV0), serDeProvider.getSerializer(new AirbyteVersion("0.1.0")));
    assertEquals(Optional.of(serV1), serDeProvider.getSerializer(new AirbyteVersion("1.0.0")));
    assertEquals(Optional.empty(), serDeProvider.getSerializer(new AirbyteVersion("3.2.0")));
  }

  @Test
  void testRegisterDeserializerShouldFailOnVersionCollision() {
    AirbyteMessageDeserializer<?> deser = buildDeserializer(new AirbyteVersion("0.2.0"));
    assertThrows(RuntimeException.class, () -> {
      serDeProvider.registerDeserializer(deser);
    });
  }

  @Test
  void testRegisterSerializerShouldFailOnVersionCollision() {
    AirbyteMessageSerializer<?> ser = buildSerializer(new AirbyteVersion("0.5.0"));
    assertThrows(RuntimeException.class, () -> {
      serDeProvider.registerSerializer(ser);
    });
  }

  private <T> AirbyteMessageDeserializer<T> buildDeserializer(AirbyteVersion version) {
    final AirbyteMessageDeserializer<T> deser = mock(AirbyteMessageDeserializer.class);
    when(deser.getTargetVersion()).thenReturn(version);
    return deser;
  }

  private <T> AirbyteMessageSerializer<T> buildSerializer(AirbyteVersion version) {
    final AirbyteMessageSerializer<T> ser = mock(AirbyteMessageSerializer.class);
    when(ser.getTargetVersion()).thenReturn(version);
    return ser;
  }

}
