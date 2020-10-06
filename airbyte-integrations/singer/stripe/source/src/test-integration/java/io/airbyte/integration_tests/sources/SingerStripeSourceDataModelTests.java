/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.singer.SingerMessage;
import io.airbyte.workers.protocols.singer.SingerProtocolPredicate;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class SingerStripeSourceDataModelTests {

  @Test
  void canDeserializeStripeCatalog() throws IOException {
    final String input = MoreResources.readResource("stripe_catalog.json");
    final String canDeserializeStripeSchemaMessage = Jsons.serialize(Jsons.deserialize(input, SingerCatalog.class));

    final JsonNode deserialize = Jsons.deserialize(input);
    // our deserializer converts `type: "object"` => `type: ["object"]`. both are valid jsonschema.
    ((ObjectNode) deserialize.get("streams").get(1).get("schema")).putArray("type").add("object");

    assertEquals(deserialize, Jsons.deserialize(canDeserializeStripeSchemaMessage));
  }

  @Test
  void canDeserializeStripeSchemaMessage() throws IOException {
    final String input = MoreResources.readResource("stripe_schema_message.json");
    final String reserialized = Jsons.serialize(Jsons.deserialize(input, SingerMessage.class));

    assertEquals(Jsons.deserialize(input), Jsons.deserialize(reserialized));
  }

  @Test
  void stripeSchemaMessageIsValid() throws IOException {
    final String input = MoreResources.readResource("stripe_schema_message.json");
    final SingerProtocolPredicate singerProtocolPredicate = new SingerProtocolPredicate();
    assertTrue(singerProtocolPredicate.test(Jsons.deserialize(input)));
  }

}
