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
import io.airbyte.config.Schema;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.workers.protocols.singer.SingerCatalogConverters;
import io.airbyte.workers.protocols.singer.SingerProtocolPredicate;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class SingerExchangeRatesApiSourceDataModelTest {

  @Test
  void testDeserializeCatalog() throws IOException {
    final String input = MoreResources.readResource("catalog.json");

    final JsonNode expected = Jsons.deserialize(input);
    // our deserializer converts `type: "object"` => `type: ["object"]`. both are valid jsonschema.
    Jsons.mutateTypeToArrayStandard(expected.get("streams").get(0).get("schema"));
    expected.get("streams")
        .get(0)
        .get("schema")
        .get("properties")
        .forEach(Jsons::mutateTypeToArrayStandard);

    final SingerCatalog catalog = Jsons.deserialize(input, SingerCatalog.class);

    // test deserialize / serialize
    assertEquals(expected, Jsons.deserialize(Jsons.serialize(catalog)));

    // test after applying airbyte schema.
    final Schema airbyteSchema = SingerCatalogConverters.toAirbyteSchema(catalog);
    final SingerCatalog catalogWithSchemaApplied = SingerCatalogConverters.applySchemaToDiscoveredCatalog(catalog, airbyteSchema);

    // we end up adding an empty metadata field.
    JsonNode expectedAfterSchemaApplied = Jsons.clone(expected);
    ((ObjectNode) expectedAfterSchemaApplied.get("streams").get(0)).putArray("metadata");
    assertEquals(expectedAfterSchemaApplied, Jsons.deserialize(Jsons.serialize(catalogWithSchemaApplied)));
  }

  @Test
  void stripeSchemaMessageIsValid() throws IOException {
    final String input = MoreResources.readResource("schema_message.json");
    assertTrue(new SingerProtocolPredicate().test(Jsons.deserialize(input)));
  }

}
