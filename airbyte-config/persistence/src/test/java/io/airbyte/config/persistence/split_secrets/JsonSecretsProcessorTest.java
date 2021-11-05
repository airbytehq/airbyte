/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

public class JsonSecretsProcessorTest {

  private static final JsonNode SCHEMA_ONE_LAYER = Jsons.deserialize(
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

  private static final JsonNode SCHEMA_INNER_OBJECT = Jsons.deserialize(
      "{\n"
          + "    \"type\": \"object\",\n"
          + "    \"properties\": {\n"
          + "      \"warehouse\": {\n"
          + "        \"type\": \"string\"\n"
          + "      },\n"
          + "      \"loading_method\": {\n"
          + "        \"type\": \"object\",\n"
          + "        \"oneOf\": [\n"
          + "          {\n"
          + "            \"properties\": {}\n"
          + "          },\n"
          + "          {\n"
          + "            \"properties\": {\n"
          + "              \"s3_bucket_name\": {\n"
          + "                \"type\": \"string\"\n"
          + "              },\n"
          + "              \"secret_access_key\": {\n"
          + "                \"type\": \"string\",\n"
          + "                \"airbyte_secret\": true\n"
          + "              }\n"
          + "            }\n"
          + "          }\n"
          + "        ]\n"
          + "      }\n"
          + "    }\n"
          + "  }");

  JsonSecretsProcessor processor = new JsonSecretsProcessor();

  @Test
  public void testMaskSecrets() {
    final JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", "verysecret").build());

    final JsonNode sanitized = processor.maskSecrets(obj, SCHEMA_ONE_LAYER);

    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", JsonSecretsProcessor.SECRETS_MASK)
        .put("secret2", JsonSecretsProcessor.SECRETS_MASK).build());
    assertEquals(expected, sanitized);
  }

  @Test
  public void testMaskSecretsNotInObj() {
    final JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2).build());

    final JsonNode actual = processor.maskSecrets(obj, SCHEMA_ONE_LAYER);

    // Didn't have secrets, no fields should have been impacted.
    assertEquals(obj, actual);
  }

  @Test
  public void testMaskSecretInnerObject() {
    final JsonNode oneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", "secret").build());
    final JsonNode base = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", oneOf).build());

    final JsonNode actual = processor.maskSecrets(base, SCHEMA_INNER_OBJECT);

    final JsonNode expectedOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", JsonSecretsProcessor.SECRETS_MASK)
        .build());
    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", expectedOneOf).build());

    assertEquals(expected, actual);
  }

  @Test
  public void testMaskSecretNotInInnerObject() {
    final JsonNode base = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house").build());

    final JsonNode actual = processor.maskSecrets(base, SCHEMA_INNER_OBJECT);

    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house").build());

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecrets() {
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("additional_field", "dont_copy_me")
        .put("secret1", "donttellanyone")
        .put("secret2", "updateme")
        .build());

    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", JsonSecretsProcessor.SECRETS_MASK)
        .put("secret2", "newvalue")
        .build());

    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", "newvalue")
        .build());

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretsNotInSrc() {
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("additional_field", "dont_copy_me")
        .build());

    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", JsonSecretsProcessor.SECRETS_MASK)
        .build());

    final JsonNode expected = dst.deepCopy();
    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretInnerObject() {
    final JsonNode srcOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", "secret")
        .put("additional_field", "dont_copy_me")
        .build());
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", srcOneOf).build());

    final JsonNode dstOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", JsonSecretsProcessor.SECRETS_MASK)
        .build());
    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", dstOneOf).build());

    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_INNER_OBJECT);

    final JsonNode expectedOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", "secret").build());
    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", expectedOneOf).build());

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretNotInSrcInnerObject() {
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house").build());

    final JsonNode dstOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", JsonSecretsProcessor.SECRETS_MASK)
        .build());
    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", dstOneOf).build());

    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_INNER_OBJECT);
    final JsonNode expected = dst.deepCopy();

    assertEquals(expected, actual);
  }

}
