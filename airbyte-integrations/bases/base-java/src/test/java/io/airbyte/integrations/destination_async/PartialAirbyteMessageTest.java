package io.airbyte.integrations.destination_async;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.time.Instant;

public class PartialAirbyteMessageTest {

    @Test
    void testDeserializeRecord() {
        final var serializedRec = Jsons.serialize(new AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(new AirbyteRecordMessage()
                        .withStream("users")
                        .withNamespace("public")
                        .withEmittedAt(Instant.now().toEpochMilli())
                        .withData(Jsons.jsonNode("data"))));

        System.out.println(serializedRec);
        final var rec = Jsons.tryDeserialize(serializedRec, PartialAirbyteMessage.class).get();
        Assertions.assertEquals(AirbyteMessage.Type.RECORD, rec.getType());
        Assertions.assertEquals("users", rec.getRecord().getStream());
        Assertions.assertEquals("public", rec.getRecord().getNamespace());
        Assertions.assertEquals("\"data\"", rec.getRecord().getData().toString());
    }
}
