/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.constants.AirbyteSecretConstants;
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

@SuppressWarnings({"PMD.CloseResource", "PMD.UseProperClassLoader", "PMD.JUnitTestsShouldIncludeAssert"})
class JsonSecretsProcessorTest {

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

  private static final String FIELD_1 = "field1";
  private static final String VALUE_1 = "value1";
  private static final String FIELD_2 = "field2";
  private static final String ADDITIONAL_FIELD = "additional_field";
  private static final String DONT_COPY_ME = "dont_copy_me";
  private static final String DONT_TELL_ANYONE = "donttellanyone";
  private static final String SECRET_1 = "secret1";
  private static final String SECRET_2 = "secret2";
  private static final String NAME = "name";
  private static final String S3_BUCKET_NAME = "s3_bucket_name";
  private static final String SECRET_ACCESS_KEY = "secret_access_key";
  private static final String HOUSE = "house";
  private static final String WAREHOUSE = "warehouse";
  private static final String LOADING_METHOD = "loading_method";
  private static final String ARRAY = "array";
  private static final String ARRAY_OF_ONEOF = "array_of_oneof";
  private static final String NESTED_OBJECT = "nested_object";
  private static final String NESTED_ONEOF = "nested_oneof";
  private static final String ONE_OF_SECRET = "oneof_secret";
  private static final String ONE_OF = "oneof";
  private static final String OPTIONAL_PASSWORD = "optional_password";
  private static final String POSTGRES_SSH_KEY = "postgres_ssh_key";
  private static final String SIMPLE = "simple";

  private JsonSecretsProcessor processor;

  @BeforeEach
  public void setup() {
    processor = JsonSecretsProcessor.builder()
        .copySecrets(true)
        .build();
  }

  @Test
  void testCopySecrets() {
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put(FIELD_1, VALUE_1)
        .put(FIELD_2, 2)
        .put(ADDITIONAL_FIELD, DONT_COPY_ME)
        .put(SECRET_1, DONT_TELL_ANYONE)
        .put(SECRET_2, "updateme")
        .build());

    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put(FIELD_1, VALUE_1)
        .put(FIELD_2, 2)
        .put(SECRET_1, AirbyteSecretConstants.SECRETS_MASK)
        .put(SECRET_2, "newvalue")
        .build());

    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put(FIELD_1, VALUE_1)
        .put(FIELD_2, 2)
        .put(SECRET_1, DONT_TELL_ANYONE)
        .put(SECRET_2, "newvalue")
        .build());

    assertEquals(expected, actual);
  }

  @Test
  void testCopySecretsNotInSrc() {
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put(FIELD_1, VALUE_1)
        .put(FIELD_2, 2)
        .put(ADDITIONAL_FIELD, DONT_COPY_ME)
        .build());

    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put(FIELD_1, VALUE_1)
        .put(FIELD_2, 2)
        .put(SECRET_1, AirbyteSecretConstants.SECRETS_MASK)
        .build());

    final JsonNode expected = dst.deepCopy();
    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

    assertEquals(expected, actual);
  }

  @Test
  void testCopySecretInnerObject() {
    final JsonNode srcOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put(S3_BUCKET_NAME, NAME)
        .put(SECRET_ACCESS_KEY, "secret")
        .put(ADDITIONAL_FIELD, DONT_COPY_ME)
        .build());
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put(WAREHOUSE, HOUSE)
        .put("loading_method", srcOneOf).build());

    final JsonNode dstOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put(S3_BUCKET_NAME, NAME)
        .put(SECRET_ACCESS_KEY, AirbyteSecretConstants.SECRETS_MASK)
        .build());
    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put(WAREHOUSE, HOUSE)
        .put(LOADING_METHOD, dstOneOf).build());

    final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_INNER_OBJECT);

    final JsonNode expectedOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put(S3_BUCKET_NAME, NAME)
        .put(SECRET_ACCESS_KEY, "secret").build());
    final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put(WAREHOUSE, HOUSE)
        .put(LOADING_METHOD, expectedOneOf).build());

    assertEquals(expected, actual);
  }

  @Test
  void testCopySecretNotInSrcInnerObject() {
    final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put(WAREHOUSE, HOUSE).build());

    final JsonNode dstOneOf = Jsons.jsonNode(ImmutableMap.builder()
        .put(S3_BUCKET_NAME, NAME)
        .put(SECRET_ACCESS_KEY, AirbyteSecretConstants.SECRETS_MASK)
        .build());
    final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put(WAREHOUSE, HOUSE)
        .put(LOADING_METHOD, dstOneOf).build());

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

    processor.copySecrets(src, dst, ONE_OF_WITH_SAME_KEY_IN_SUB_SCHEMAS);
  }

  private static Stream<Arguments> scenarioProvider() {
    return Stream.of(
        Arguments.of(ARRAY, true),
        Arguments.of(ARRAY, false),
        Arguments.of(ARRAY_OF_ONEOF, true),
        Arguments.of(ARRAY_OF_ONEOF, false),
        Arguments.of(NESTED_OBJECT, true),
        Arguments.of(NESTED_OBJECT, false),
        Arguments.of(NESTED_ONEOF, true),
        Arguments.of(NESTED_ONEOF, false),
        Arguments.of(ONE_OF, true),
        Arguments.of(ONE_OF, false),
        Arguments.of(ONE_OF_SECRET, true),
        Arguments.of(ONE_OF_SECRET, false),
        Arguments.of(OPTIONAL_PASSWORD, true),
        Arguments.of(OPTIONAL_PASSWORD, false),
        Arguments.of(POSTGRES_SSH_KEY, true),
        Arguments.of(POSTGRES_SSH_KEY, false),
        Arguments.of(SIMPLE, true),
        Arguments.of(SIMPLE, false),
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
  void copiesSecretsInNestedNonCombinationNode() throws JsonProcessingException {
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
  void doesNotCopySecretsInNestedNonCombinationNodeWhenDestinationMissing() throws JsonProcessingException {
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

  @Test
  void testCopySecretsWithTopLevelOneOf() {
    final JsonNode schema = Jsons.deserialize("""
                                              {
                                                  "$schema": "http://json-schema.org/draft-07/schema#",
                                                  "title": "E2E Test Destination Spec",
                                                  "type": "object",
                                                  "oneOf": [
                                                    {
                                                      "title": "Silent",
                                                      "required": ["type"],
                                                      "properties": {
                                                        "a_secret": {
                                                          "type": "string",
                                                          "airbyte_secret": true
                                                        }
                                                      }
                                                    },
                                                    {
                                                      "title": "Throttled",
                                                      "required": ["type", "millis_per_record"],
                                                      "properties": {
                                                        "type": {
                                                          "type": "string",
                                                          "const": "THROTTLED",
                                                          "default": "THROTTLED"
                                                        },
                                                        "millis_per_record": {
                                                          "description": "Number of milli-second to pause in between records.",
                                                          "type": "integer"
                                                        }
                                                      }
                                                    }
                                                  ]
                                                }
                                              """);

    final JsonNode source = Jsons.deserialize("""
                                              {
                                                "type": "THROTTLED",
                                                "a_secret": "woot"
                                              }
                                              """);

    final JsonNode destination = Jsons.deserialize("""
                                                   {
                                                     "type": "THROTTLED",
                                                     "a_secret": "**********"
                                                   }
                                                   """);

    final JsonNode result = processor.copySecrets(source, destination, schema);
    final JsonNode expected = Jsons.deserialize("""
                                                {
                                                  "type": "THROTTLED",
                                                  "a_secret": "woot"
                                                }
                                                """);

    assertEquals(expected, result);
  }

  @Nested
  class NoOpTest {

    @BeforeEach
    public void setup() {
      processor = JsonSecretsProcessor.builder()
          .copySecrets(false)
          .build();
    }

    @Test
    void testCopySecrets() {
      final JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
          .put(FIELD_1, VALUE_1)
          .put(FIELD_2, 2)
          .put(ADDITIONAL_FIELD, DONT_COPY_ME)
          .put(SECRET_1, DONT_TELL_ANYONE)
          .put(SECRET_2, "updateme")
          .build());

      final JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
          .put(FIELD_1, VALUE_1)
          .put(FIELD_2, 2)
          .put(SECRET_1, AirbyteSecretConstants.SECRETS_MASK)
          .put(SECRET_2, "newvalue")
          .build());

      final JsonNode actual = processor.copySecrets(src, dst, SCHEMA_ONE_LAYER);

      final JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
          .put(FIELD_1, VALUE_1)
          .put(FIELD_2, 2)
          .put(ADDITIONAL_FIELD, DONT_COPY_ME)
          .put(SECRET_1, DONT_TELL_ANYONE)
          .put(SECRET_2, "updateme")
          .build());

      assertEquals(expected, actual);
    }

    private static Stream<Arguments> scenarioProvider() {
      return Stream.of(
          Arguments.of(ARRAY, true),
          Arguments.of(ARRAY, false),
          Arguments.of(ARRAY_OF_ONEOF, true),
          Arguments.of(ARRAY_OF_ONEOF, false),
          Arguments.of(NESTED_OBJECT, true),
          Arguments.of(NESTED_OBJECT, false),
          Arguments.of(NESTED_ONEOF, true),
          Arguments.of(NESTED_ONEOF, false),
          Arguments.of(ONE_OF, true),
          Arguments.of(ONE_OF, false),
          Arguments.of(OPTIONAL_PASSWORD, true),
          Arguments.of(OPTIONAL_PASSWORD, false),
          Arguments.of(POSTGRES_SSH_KEY, true),
          Arguments.of(POSTGRES_SSH_KEY, false),
          Arguments.of(SIMPLE, true),
          Arguments.of(SIMPLE, false));
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

  }

}
