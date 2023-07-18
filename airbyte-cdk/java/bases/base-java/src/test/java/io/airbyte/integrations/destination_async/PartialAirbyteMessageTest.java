/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class PartialAirbyteMessageTest {

  @Test
  void testDeserializeRecord() {
    final long emittedAt = Instant.now().toEpochMilli();
    final var serializedRec = Jsons.serialize(new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream("users")
            .withNamespace("public")
            .withEmittedAt(emittedAt)
            .withData(Jsons.jsonNode("data"))));

    final var rec = Jsons.tryDeserialize(serializedRec, PartialAirbyteMessage.class).get();
    Assertions.assertEquals(AirbyteMessage.Type.RECORD, rec.getType());
    Assertions.assertEquals("users", rec.getRecord().getStream());
    Assertions.assertEquals("public", rec.getRecord().getNamespace());
    Assertions.assertEquals("\"data\"", rec.getRecord().getData().toString());
    Assertions.assertEquals(emittedAt, rec.getRecord().getEmittedAt());
  }

  @Test
  void testDeserializeState() {
    final var serializedState = Jsons.serialize(new io.airbyte.protocol.models.AirbyteMessage()
        .withType(io.airbyte.protocol.models.AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withStream(
            new AirbyteStreamState().withStreamDescriptor(
                new StreamDescriptor().withName("user").withNamespace("public"))
                .withStreamState(Jsons.jsonNode("data")))
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)));

    final var rec = Jsons.tryDeserialize(serializedState, PartialAirbyteMessage.class).get();
    Assertions.assertEquals(AirbyteMessage.Type.STATE, rec.getType());

    final var streamDesc = rec.getState().getStream().getStreamDescriptor();
    Assertions.assertEquals("user", streamDesc.getName());
    Assertions.assertEquals("public", streamDesc.getNamespace());
    Assertions.assertEquals(io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType.STREAM, rec.getState().getType());
  }

  @Test
  void testGarbage() {
    final var badSerialization = "messed up data";

    final var rec = Jsons.tryDeserialize(badSerialization, PartialAirbyteMessage.class);
    Assertions.assertTrue(rec.isEmpty());
  }

}
