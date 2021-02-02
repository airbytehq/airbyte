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

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

public class JsonSecretsProcessorTest {

  private static final JsonNode SCHEMA = Jsons.deserialize(
      "{\n"
          + "  \"properties\": {\n"
          + "    \"secret1\": {\n"
          + "      \"type\": \"string\",\n"
          + "      \"airbyte_secret\": true\n"
          + "    },\n"
          + "    \"secret2\": {\n"
          + "      \"type\": \"string\",\n"
          + "      \"airbyte_secret\": \"true\"\n"
          + "    },\n"
          + "    \"field1\": {\n"
          + "      \"type\": \"string\"\n"
          + "    },\n"
          + "    \"field2\": {\n"
          + "      \"type\": \"number\"\n"
          + "    }\n"
          + "  }\n"
          + "}\n");

  JsonSecretsProcessor processor = new JsonSecretsProcessor();

  @Test
  public void testMaskSecrets() {
    JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", "verysecret").build());

    JsonNode sanitized = processor.maskSecrets(obj, SCHEMA);

    JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", JsonSecretsProcessor.SECRETS_MASK)
        .put("secret2", JsonSecretsProcessor.SECRETS_MASK).build());
    assertEquals(expected, sanitized);
  }

  @Test
  public void testMaskSecretsNotInObj() {
    JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2).build());

    JsonNode actual = processor.maskSecrets(obj, SCHEMA);

    // Didn't have secrets, no fields should have been impacted.
    assertEquals(obj, actual);
  }

  @Test
  public void testCopySecrets() {
    JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("additional_field", "dont_copy_me")
        .put("secret1", "donttellanyone")
        .put("secret2", "updateme")
        .build());

    JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", JsonSecretsProcessor.SECRETS_MASK)
        .put("secret2", "newvalue")
        .build());

    JsonNode actual = processor.copySecrets(src, dst, SCHEMA);

    JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", "newvalue")
        .build());

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretsNotInSrc() {
    JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("additional_field", "dont_copy_me")
        .build());

    JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .build());

    JsonNode expected = dst.deepCopy();
    JsonNode actual = processor.copySecrets(src, dst, SCHEMA);

    assertEquals(expected, actual);
  }

}
