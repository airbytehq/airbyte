/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import io.airbyte.cdk.integrations.destination_async.dto.AirbyteMessage.AirbyteRecordMessageWrapper;
import io.airbyte.cdk.integrations.destination_async.dto.AirbyteModifiedData;
import io.airbyte.cdk.integrations.destination_async.dto.AirbyteRecordMessageDeserializer;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason;
import java.time.Instant;
import java.util.List;
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
  void testDeserializeRecord2() throws JsonProcessingException {
    ObjectMapper objectMapper = MoreMappers.initMapper();
    SimpleModule module = new SimpleModule();
    module.addDeserializer(io.airbyte.cdk.integrations.destination_async.dto.AirbyteRecordMessage.class, new AirbyteRecordMessageDeserializer());
    objectMapper.registerModule(module);
    String data = "{\"integer\": 1, \"string\": \"string\", \"boolean\": true, \"array\": [1, 2, 3], \"object\": {\"key\": \"value\" }}";
    JsonNode dataNode = Jsons.deserialize(data);
    final long emittedAt = Instant.now().toEpochMilli();
    final var serializedRec = Jsons.serialize(new AirbyteMessage()
                                                  .withType(AirbyteMessage.Type.RECORD)
                                                  .withRecord(new AirbyteRecordMessage()
                                                                  .withStream("users")
                                                                  .withNamespace("public")
                                                                  .withEmittedAt(emittedAt)
                                                                  .withData(dataNode)
                                                                  .withMeta(
                                                                      new AirbyteRecordMessageMeta()
                                                                          .withChanges(
                                                                              List.of(
                                                                                  new AirbyteRecordMessageMetaChange()
                                                                                      .withChange(Change.NULLED).withField("object")
                                                                                      .withReason(Reason.DESTINATION_SERIALIZATION_ERROR)
                                                                              )
                                                                          )
                                                                  )
                                                  )
    );


    final var rec = objectMapper.readValue(serializedRec, io.airbyte.cdk.integrations.destination_async.dto.AirbyteMessage.class);
    System.out.println(rec);
    final var serializedState = Jsons.serialize(new io.airbyte.protocol.models.AirbyteMessage()
                                                    .withType(io.airbyte.protocol.models.AirbyteMessage.Type.STATE)
                                                    .withState(new AirbyteStateMessage().withStream(
                                                            new AirbyteStreamState().withStreamDescriptor(
                                                                    new StreamDescriptor().withName("user").withNamespace("public"))
                                                                .withStreamState(Jsons.jsonNode("data")))
                                                                   .withType(AirbyteStateMessage.AirbyteStateType.STREAM)));

    final var state = Jsons.tryDeserialize(serializedState, io.airbyte.cdk.integrations.destination_async.dto.AirbyteMessage.class).get();
    System.out.println(state);
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
