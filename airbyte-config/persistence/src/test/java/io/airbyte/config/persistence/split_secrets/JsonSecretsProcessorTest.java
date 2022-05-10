/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.InputStream;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class JsonSecretsProcessorTest {

  private static final JsonNode SCHEMA_ONE_LAYER = Jsons.deserialize(
      """
      {
        "type": "object",  "properties": {
          "secret1": {
            "type": "string",
            "airbyte_secret": true
          },
          "secret2": {
            "type": "string",
            "airbyte_secret": "true"
          },
          "field1": {
            "type": "string"
          },
          "field2": {
            "type": "number"
          }
        }
      }
      """);

  private static final JsonNode SCHEMA_WITH_ARRAY = Jsons.deserialize(
      """
      {
        "type": "object",  "properties": {
          "secret1": {
            "type": "array",      "items": {
              "type": "string",
              "airbyte_secret": true
            }
          },
          "secret2": {
            "type": "string",
            "airbyte_secret": "true"
          },
          "field1": {
            "type": "string"
          },
          "field2": {
            "type": "number"
          }
        }
      }
      """);

  private static final JsonNode SCHEMA_INNER_OBJECT = Jsons.deserialize(
      """
      {
          "type": "object",
          "properties": {
            "warehouse": {
              "type": "string"
            },
            "loading_method": {
              "type": "object",
              "oneOf": [
                {
                  "properties": {}
                },
                {
                  "properties": {
                    "s3_bucket_name": {
                      "type": "string"
                    },
                    "secret_access_key": {
                      "type": "string",
                      "airbyte_secret": true
                    }
                  }
                }
              ]
            }
          }
        }""");

  private static final JsonNode ONE_OF_WITH_SAME_KEY_IN_SUB_SCHEMAS = Jsons.deserialize(
      """
      {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "title": "S3 Destination Spec",
          "type": "object",
          "required": [
            "client_id",
            "format"
          ],
          "additionalProperties": false,
          "properties": {
            "client_id": {
              "title": "client it",
              "type": "string",
              "default": ""
            },
            "format": {
              "title": "Output Format",
              "type": "object",
              "description": "Output data format",
              "oneOf": [
                {
                  "title": "Avro: Apache Avro",
                  "required": ["format_type", "compression_codec"],
                  "properties": {
                    "format_type": {
                      "type": "string",
                      "enum": ["Avro"],
                      "default": "Avro"
                    },
                    "compression_codec": {
                      "title": "Compression Codec",
                      "description": "The compression algorithm used to compress data. Default to no compression.",
                      "type": "object",
                      "oneOf": [
                        {
                          "title": "no compression",
                          "required": ["codec"],
                          "properties": {
                            "codec": {
                              "type": "string",
                              "enum": ["no compression"],
                              "default": "no compression"
                            }
                          }
                        },
                        {
                          "title": "Deflate",
                          "required": ["codec", "compression_level"],
                          "properties": {
                            "codec": {
                              "type": "string",
                              "enum": ["Deflate"],
                              "default": "Deflate"
                            },
                            "compression_level": {
                              "type": "integer",
                              "default": 0,
                              "minimum": 0,
                              "maximum": 9
                            }
                          }
                        }
                      ]
                    }
                  }
                },
                {
                  "title": "Parquet: Columnar Storage",
                  "required": ["format_type"],
                  "properties": {
                    "format_type": {
                      "type": "string",
                      "enum": ["Parquet"],
                      "default": "Parquet"
                    },
                    "compression_codec": {
                      "type": "string",
                      "enum": [
                        "UNCOMPRESSED",
                        "GZIP"
                      ],
                      "default": "UNCOMPRESSED"
                    }
                  }
                }
              ]
            }
          }
        }""");

  private JsonSecretsProcessor processor;

  @BeforeEach
  public void setup() {
    processor = JsonSecretsProcessor.builder()
        .copySecrets(true)
        .maskSecrets(true)
        .build();
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

    final JsonNode actual = processor.copySecrets(src, dst, ONE_OF_WITH_SAME_KEY_IN_SUB_SCHEMAS);
  }

  private static Stream<Arguments> scenarioProvider() {
    return Stream.of(
        Arguments.of("array", true),
        Arguments.of("array", false),
        Arguments.of("array_of_oneof", true),
        Arguments.of("array_of_oneof", false),
        Arguments.of("nested_object", true),
        Arguments.of("nested_object", false),
        Arguments.of("nested_oneof", true),
        Arguments.of("nested_oneof", false),
        Arguments.of("oneof", true),
        Arguments.of("oneof", false),
        Arguments.of("optional_password", true),
        Arguments.of("optional_password", false),
        Arguments.of("postgres_ssh_key", true),
        Arguments.of("postgres_ssh_key", false),
        Arguments.of("simple", true),
        Arguments.of("simple", false),
        Arguments.of("enum", false));
  }

  @ParameterizedTest
  @MethodSource("scenarioProvider")
  void testSecretScenario(final String folder, final boolean partial) throws IOException {
    final ObjectMapper objectMapper = new ObjectMapper();

    final InputStream specIs = getClass().getClassLoader().getResourceAsStream(folder + "/spec.json");
    final JsonNode specs = objectMapper.readTree(specIs);

    final String inputFilePath = folder + (partial ? "/partial_config.json" : "/full_config.json");
    final InputStream inputIs = getClass().getClassLoader().getResourceAsStream(inputFilePath);
    final JsonNode input = objectMapper.readTree(inputIs);

    final String expectedFilePath = folder + "/expected.json";
    final InputStream expectedIs = getClass().getClassLoader().getResourceAsStream(expectedFilePath);
    final JsonNode expected = objectMapper.readTree(expectedIs);

    final JsonNode actual = processor.prepareSecretsForOutput(input, specs);
    assertEquals(expected, actual);
  }

  // todo (cgardens) - example of a case that is not properly handled. we should explicitly call out
  // that this type of jsonschema object is not allowed to do secrets.
  // private static Stream<Arguments> scenarioProvider2() {
  // return Stream.of(
  // Arguments.of("array2", true),
  // Arguments.of("array2", false));
  // }
  //
  // @ParameterizedTest
  // @MethodSource("scenarioProvider2")
  // void testSecretScenario2(final String folder, final boolean partial) throws IOException {
  // final ObjectMapper objectMapper = new ObjectMapper();
  //
  // final InputStream specIs = getClass().getClassLoader().getResourceAsStream(folder +
  // "/spec.json");
  // final JsonNode specs = objectMapper.readTree(specIs);
  //
  // final String inputFilePath = folder + (partial ? "/partial_config.json" : "/full_config.json");
  // final InputStream inputIs = getClass().getClassLoader().getResourceAsStream(inputFilePath);
  // final JsonNode input = objectMapper.readTree(inputIs);
  //
  // final String expectedFilePath = folder + "/expected.json";
  // final InputStream expectedIs = getClass().getClassLoader().getResourceAsStream(expectedFilePath);
  // final JsonNode expected = objectMapper.readTree(expectedIs);
  //
  // final JsonNode actual = Secrets.maskAllSecrets(input, specs);
  // assertEquals(expected, actual);
  // }

  @Test
  public void copiesSecrets_inNestedNonCombinationNode() throws JsonProcessingException {
    final ObjectMapper objectMapper = new ObjectMapper();

    final JsonNode source = objectMapper.readTree(
        """
        {
          "top_level": {
            "a_secret": "hunter2"
          }
        }
        """);
    final JsonNode dest = objectMapper.readTree(
        """
        {
          "top_level": {
            "a_secret": "**********"
          }
        }
        """);
    final JsonNode schema = objectMapper.readTree(
        """
        {
          "type": "object",
          "properties": {
            "top_level": {
              "type": "object",
              "properties": {
                "a_secret": {
                  "type": "string",
                  "airbyte_secret": true
                }
              }
            }
          }
        }
        """);

    final JsonNode copied = processor.copySecrets(source, dest, schema);

    final JsonNode expected = objectMapper.readTree(
        """
        {
          "top_level": {
            "a_secret": "hunter2"
          }
        }
        """);
    assertEquals(expected, copied);
  }

  @Test
  public void doesNotCopySecrets_inNestedNonCombinationNodeWhenDestinationMissing() throws JsonProcessingException {
    final ObjectMapper objectMapper = new ObjectMapper();

    final JsonNode source = objectMapper.readTree(
        """
        {
          "top_level": {
            "a_secret": "hunter2"
          }
        }
        """);
    final JsonNode dest = objectMapper.readTree(
        """
        {
          "top_level": {
          }
        }
        """);
    final JsonNode schema = objectMapper.readTree(
        """
        {
          "type": "object",
          "properties": {
            "top_level": {
              "type": "object",
              "properties": {
                "a_secret": {
                  "type": "string",
                  "airbyte_secret": true
                }
              }
            }
          }
        }
        """);

    final JsonNode copied = processor.copySecrets(source, dest, schema);

    final JsonNode expected = objectMapper.readTree(
        """
        {
          "top_level": {
          }
        }
        """);
    assertEquals(expected, copied);
  }

  @Nested
  class NoOpTest {

    @BeforeEach
    public void setup() {
      processor = JsonSecretsProcessor.builder()
          .copySecrets(false)
          .maskSecrets(false)
          .build();
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
          .put("additional_field", "dont_copy_me")
          .put("secret1", "donttellanyone")
          .put("secret2", "updateme")
          .build());

      assertEquals(expected, actual);
    }

    private static Stream<Arguments> scenarioProvider() {
      return Stream.of(
          Arguments.of("array", true),
          Arguments.of("array", false),
          Arguments.of("array_of_oneof", true),
          Arguments.of("array_of_oneof", false),
          Arguments.of("nested_object", true),
          Arguments.of("nested_object", false),
          Arguments.of("nested_oneof", true),
          Arguments.of("nested_oneof", false),
          Arguments.of("oneof", true),
          Arguments.of("oneof", false),
          Arguments.of("optional_password", true),
          Arguments.of("optional_password", false),
          Arguments.of("postgres_ssh_key", true),
          Arguments.of("postgres_ssh_key", false),
          Arguments.of("simple", true),
          Arguments.of("simple", false));
    }

    @ParameterizedTest
    @MethodSource("scenarioProvider")
    void testSecretScenario(final String folder, final boolean partial) throws IOException {
      final ObjectMapper objectMapper = new ObjectMapper();

      final InputStream specIs = getClass().getClassLoader().getResourceAsStream(folder + "/spec.json");
      final JsonNode specs = objectMapper.readTree(specIs);

      final String inputFilePath = folder + (partial ? "/partial_config.json" : "/full_config.json");
      final InputStream inputIs = getClass().getClassLoader().getResourceAsStream(inputFilePath);
      final JsonNode input = objectMapper.readTree(inputIs);

      final String expectedFilePath = folder + (partial ? "/partial_config.json" : "/full_config.json");
      final InputStream expectedIs = getClass().getClassLoader().getResourceAsStream(expectedFilePath);
      final JsonNode expected = objectMapper.readTree(expectedIs);

      final JsonNode actual = processor.prepareSecretsForOutput(input, specs);

      assertEquals(expected, actual);
    }

  }

}
