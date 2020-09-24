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

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.workers.protocols.singer.SingerProtocolPredicate;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class SingerPostgresSourceDataModelTest {

  @Test
  void testDeserializeCatalog() throws IOException {
    final String catalogString = MoreResources.readResource("catalog.json");
    final SingerCatalog singerCatalog = Jsons.deserialize(catalogString, SingerCatalog.class);
    final String reserialized = Jsons.serialize(singerCatalog);

    final JsonNode expected = Jsons.deserialize(catalogString);
    final JsonNode actual = Jsons.deserialize(reserialized);
    Jsons.mutateTypeToArrayStandard(expected.get("streams").get(0).get("schema"));
    expected.get("streams")
        .get(0)
        .get("schema")
        .get("properties")
        .forEach(Jsons::mutateTypeToArrayStandard);

    assertEquals(expected, actual);
  }

  @Test
  void stripeSchemaMessageIsValid() throws IOException {
    final String input = MoreResources.readResource("schema_message.json");
    assertTrue(new SingerProtocolPredicate().test(Jsons.deserialize(input)));
  }

}
