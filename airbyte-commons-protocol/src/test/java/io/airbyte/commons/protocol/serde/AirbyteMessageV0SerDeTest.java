/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.net.URI;
import java.net.URISyntaxException;
import org.junit.jupiter.api.Test;

class AirbyteMessageV0SerDeTest {

  @Test
  void v0SerDeRoundTripTest() throws URISyntaxException {
    final AirbyteMessageV0Deserializer deser = new AirbyteMessageV0Deserializer();
    final AirbyteMessageV0Serializer ser = new AirbyteMessageV0Serializer();

    final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.SPEC)
        .withSpec(
            new ConnectorSpecification()
                .withProtocolVersion("0.3.0")
                .withDocumentationUrl(new URI("file:///tmp/doc")));

    final String serializedMessage = ser.serialize(message);
    final AirbyteMessage deserializedMessage = deser.deserialize(Jsons.deserialize(serializedMessage));

    assertEquals(message, deserializedMessage);
  }

}
