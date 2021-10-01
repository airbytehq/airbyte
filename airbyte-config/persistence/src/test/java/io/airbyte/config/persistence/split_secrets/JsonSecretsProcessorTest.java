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
    JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", "verysecret").build());

    JsonNode sanitized = processor.maskSecrets(obj, SCHEMA_ONE_LAYER);

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

    JsonNode actual = processor.maskSecrets(obj, SCHEMA_ONE_LAYER);

    // Didn't have secrets, no fields should have been impacted.
    assertEquals(obj, actual);
  }

  @Test
  public void testMaskSecretInnerObject() {
    JsonNode oneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", "secret").build());
    JsonNode base = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", oneOf).build());

    JsonNode actual = processor.maskSecrets(base, SCHEMA_INNER_OBJECT);

    JsonNode expectedOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", JsonSecretsProcessor.SECRETS_MASK)
        .build());
    JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", expectedOneOf).build());

    assertEquals(expected, actual);
  }

  @Test
  public void testMaskSecretNotInInnerObject() {
    JsonNode base = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house").build());

    JsonNode actual = processor.maskSecrets(base, SCHEMA_INNER_OBJECT);

    JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house").build());

    assertEquals(expected, actual);
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

    JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

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
        .put("secret1", JsonSecretsProcessor.SECRETS_MASK)
        .build());

    JsonNode expected = dst.deepCopy();
    JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretInnerObject() {
    JsonNode srcOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", "secret")
        .put("additional_field", "dont_copy_me")
        .build());
    JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", srcOneOf).build());

    JsonNode dstOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", JsonSecretsProcessor.SECRETS_MASK)
        .build());
    JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", dstOneOf).build());

    JsonNode actual = processor.copySecrets(src, dst, SCHEMA_INNER_OBJECT);

    JsonNode expectedOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", "secret").build());
    JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", expectedOneOf).build());

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretNotInSrcInnerObject() {
    JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house").build());

    JsonNode dstOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put("s3_bucket_name", "name")
        .put("secret_access_key", JsonSecretsProcessor.SECRETS_MASK)
        .build());
    JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("warehouse", "house")
        .put("loading_method", dstOneOf).build());

    JsonNode actual = processor.copySecrets(src, dst, SCHEMA_INNER_OBJECT);
    JsonNode expected = dst.deepCopy();

    assertEquals(expected, actual);
  }

}
