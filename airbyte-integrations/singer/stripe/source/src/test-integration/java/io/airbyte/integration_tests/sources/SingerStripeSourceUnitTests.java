package io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.singer.SingerMessage;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class SingerStripeSourceUnitTests {
  @Test
  void canDeserializeStripeCatalog() throws IOException {
    final String input = MoreResources.readResource("stripe_catalog.json");
    final String canDeserializeStripeSchemaMessage = Jsons.serialize(Jsons.deserialize(input, SingerCatalog.class));
    assertEquals(Jsons.deserialize(input), Jsons.deserialize(canDeserializeStripeSchemaMessage));
  }

  @Test
  void canDeserializeStripeSchemaMessage() throws IOException {
    final String input = MoreResources.readResource("stripe_schema_message.json");
    final String reserialized = Jsons.serialize(Jsons.deserialize(input, SingerMessage.class));

    assertEquals(Jsons.deserialize(input), Jsons.deserialize(reserialized));
  }

// todo (cgardens) - WIP, seems like the validation in the worker does not play well with the custom
//  deserializer. it marks the type as object when really it is going to be an array. while the
//  generate pojo is correct (using the custom serializer) the validator doesn't understand this
//  annotation and fails because these fields are not objects.
// $.schema.type: array found, object expected
// $.schema.properties.sources.anyOf: array found, object expected
//  @Test
//  void stripeSchemaMessageIsValid() throws IOException {
//    final String input = MoreResources.readResource("stripe_schema_message.json");
//    final SingerProtocolPredicate singerProtocolPredicate = new SingerProtocolPredicate();
//    assertTrue(singerProtocolPredicate.test(Jsons.deserialize(input)));
//  }

}
