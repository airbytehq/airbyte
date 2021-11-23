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

  private static final JsonNode ONE_OF_WITH_SAME_KEY_IN_SUB_SCHEMAS = Jsons.deserialize(
      "{\n"
          + "    \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n"
          + "    \"title\": \"S3 Destination Spec\",\n"
          + "    \"type\": \"object\",\n"
          + "    \"required\": [\n"
          + "      \"client_id\",\n"
          + "      \"format\"\n"
          + "    ],\n"
          + "    \"additionalProperties\": false,\n"
          + "    \"properties\": {\n"
          + "      \"client_id\": {\n"
          + "        \"title\": \"client it\",\n"
          + "        \"type\": \"string\",\n"
          + "        \"default\": \"\"\n"
          + "      },\n"
          + "      \"format\": {\n"
          + "        \"title\": \"Output Format\",\n"
          + "        \"type\": \"object\",\n"
          + "        \"description\": \"Output data format\",\n"
          + "        \"oneOf\": [\n"
          + "          {\n"
          + "            \"title\": \"Avro: Apache Avro\",\n"
          + "            \"required\": [\"format_type\", \"compression_codec\"],\n"
          + "            \"properties\": {\n"
          + "              \"format_type\": {\n"
          + "                \"type\": \"string\",\n"
          + "                \"enum\": [\"Avro\"],\n"
          + "                \"default\": \"Avro\"\n"
          + "              },\n"
          + "              \"compression_codec\": {\n"
          + "                \"title\": \"Compression Codec\",\n"
          + "                \"description\": \"The compression algorithm used to compress data. Default to no compression.\",\n"
          + "                \"type\": \"object\",\n"
          + "                \"oneOf\": [\n"
          + "                  {\n"
          + "                    \"title\": \"no compression\",\n"
          + "                    \"required\": [\"codec\"],\n"
          + "                    \"properties\": {\n"
          + "                      \"codec\": {\n"
          + "                        \"type\": \"string\",\n"
          + "                        \"enum\": [\"no compression\"],\n"
          + "                        \"default\": \"no compression\"\n"
          + "                      }\n"
          + "                    }\n"
          + "                  },\n"
          + "                  {\n"
          + "                    \"title\": \"Deflate\",\n"
          + "                    \"required\": [\"codec\", \"compression_level\"],\n"
          + "                    \"properties\": {\n"
          + "                      \"codec\": {\n"
          + "                        \"type\": \"string\",\n"
          + "                        \"enum\": [\"Deflate\"],\n"
          + "                        \"default\": \"Deflate\"\n"
          + "                      },\n"
          + "                      \"compression_level\": {\n"
          + "                        \"type\": \"integer\",\n"
          + "                        \"default\": 0,\n"
          + "                        \"minimum\": 0,\n"
          + "                        \"maximum\": 9\n"
          + "                      }\n"
          + "                    }\n"
          + "                  }\n"
          + "                ]\n"
          + "              }\n"
          + "            }\n"
          + "          },\n"
          + "          {\n"
          + "            \"title\": \"Parquet: Columnar Storage\",\n"
          + "            \"required\": [\"format_type\"],\n"
          + "            \"properties\": {\n"
          + "              \"format_type\": {\n"
          + "                \"type\": \"string\",\n"
          + "                \"enum\": [\"Parquet\"],\n"
          + "                \"default\": \"Parquet\"\n"
          + "              },\n"
          + "              \"compression_codec\": {\n"
          + "                \"type\": \"string\",\n"
          + "                \"enum\": [\n"
          + "                  \"UNCOMPRESSED\",\n"
          + "                  \"GZIP\"\n"
          + "                ],\n"
          + "                \"default\": \"UNCOMPRESSED\"\n"
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

  // test the case where multiple sub schemas of a oneOf contain the same key but a different type.
  @Test
  void testHandlesSameKeyInOneOf() {
    final JsonNode compressionCodecObject = Jsons.jsonNode(ImmutableMap.of(
        "codec", "no compression"));
    final JsonNode avroConfig = Jsons.jsonNode(ImmutableMap.of(
        "format_type", "Avro",
        "compression_codec", compressionCodecObject));
    final JsonNode src = Jsons.jsonNode(ImmutableMap.of(
        "client_id", "whatever",
        "format", avroConfig));

    final JsonNode parquetConfig = Jsons.jsonNode(ImmutableMap.of(
        "format_type", "Parquet",
        "compression_codec", "GZIP"));
    final JsonNode dst = Jsons.jsonNode(ImmutableMap.of(
        "client_id", "whatever",
        "format", parquetConfig));

    final JsonNode actual = new JsonSecretsProcessor().copySecrets(src, dst, ONE_OF_WITH_SAME_KEY_IN_SUB_SCHEMAS);
  }

}
