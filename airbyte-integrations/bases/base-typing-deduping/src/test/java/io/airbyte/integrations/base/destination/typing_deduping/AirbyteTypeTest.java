/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.UnsupportedOneOf;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import org.junit.jupiter.api.Test;

public class AirbyteTypeTest {

  @Test
  public void testStruct() {
    final List<String> structSchema = new ArrayList<>();
    structSchema.add("""
                     {
                       "type": "object",
                       "properties": {
                         "key1": {
                           "type": "boolean"
                         },
                         "key2": {
                           "type": "integer"
                         },
                         "key3": {
                           "type": "number",
                           "airbyte_type": "integer"
                         },
                         "key4": {
                           "type": "number"
                         },
                         "key5": {
                           "type": "string",
                           "format": "date"
                         },
                         "key6": {
                           "type": "string",
                           "format": "time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key7": {
                           "type": "string",
                           "format": "time",
                           "airbyte_type": "timestamp_with_timezone"
                         },
                         "key8": {
                           "type": "string",
                           "format": "date-time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key9": {
                           "type": "string",
                           "format": ["date-time", "foo"],
                           "airbyte_type": "timestamp_with_timezone"
                         },
                         "key10": {
                           "type": "string",
                           "format": "date-time"
                         },
                         "key11": {
                           "type": "string"
                         }
                       }
                     }
                     """);
    structSchema.add("""
                     {
                       "type": ["object"],
                       "properties": {
                         "key1": {
                           "type": ["boolean"]
                         },
                         "key2": {
                           "type": ["integer"]
                         },
                         "key3": {
                           "type": ["number"],
                           "airbyte_type": "integer"
                         },
                         "key4": {
                           "type": ["number"]
                         },
                         "key5": {
                           "type": ["string"],
                           "format": "date"
                         },
                         "key6": {
                           "type": ["string"],
                           "format": "time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key7": {
                           "type": ["string"],
                           "format": "time",
                           "airbyte_type": "timestamp_with_timezone"
                         },
                         "key8": {
                           "type": ["string"],
                           "format": "date-time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key9": {
                           "type": ["string"],
                           "format": ["date-time", "foo"],
                           "airbyte_type": "timestamp_with_timezone"
                         },
                         "key10": {
                           "type": ["string"],
                           "format": "date-time"
                         },
                         "key11": {
                           "type": ["string"]
                         }
                       }
                     }
                     """);
    structSchema.add("""
                     {
                       "type": ["null", "object"],
                       "properties": {
                         "key1": {
                           "type": ["null", "boolean"]
                         },
                         "key2": {
                           "type": ["null", "integer"]
                         },
                         "key3": {
                           "type": ["null", "number"],
                           "airbyte_type": "integer"
                         },
                         "key4": {
                           "type": ["null", "number"]
                         },
                         "key5": {
                           "type": ["null", "string"],
                           "format": "date"
                         },
                         "key6": {
                           "type": ["null", "string"],
                           "format": "time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key7": {
                           "type": ["null", "string"],
                           "format": "time",
                           "airbyte_type": "timestamp_with_timezone"
                         },
                         "key8": {
                           "type": ["null", "string"],
                           "format": "date-time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key9": {
                           "type": ["null", "string"],
                           "format": ["date-time", "foo"],
                           "airbyte_type": "timestamp_with_timezone"
                         },
                         "key10": {
                           "type": ["null", "string"],
                           "format": "date-time"
                         },
                         "key11": {
                           "type": ["null", "string"]
                         }
                       }
                     }
                     """);

    final LinkedHashMap<String, AirbyteType> propertiesMap = new LinkedHashMap<>();
    propertiesMap.put("key1", AirbyteProtocolType.BOOLEAN);
    propertiesMap.put("key2", AirbyteProtocolType.INTEGER);
    propertiesMap.put("key3", AirbyteProtocolType.INTEGER);
    propertiesMap.put("key4", AirbyteProtocolType.NUMBER);
    propertiesMap.put("key5", AirbyteProtocolType.DATE);
    propertiesMap.put("key6", AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    propertiesMap.put("key7", AirbyteProtocolType.TIME_WITH_TIMEZONE);
    propertiesMap.put("key8", AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    propertiesMap.put("key9", AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    propertiesMap.put("key10", AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    propertiesMap.put("key11", AirbyteProtocolType.STRING);

    final AirbyteType struct = new Struct(propertiesMap);
    for (final String schema : structSchema) {
      assertEquals(struct, AirbyteType.fromJsonSchema(Jsons.deserialize(schema)));
    }
  }

  @Test
  public void testEmptyStruct() {
    final List<String> structSchema = new ArrayList<>();
    structSchema.add("""
                     {
                       "type": "object"
                     }
                     """);
    structSchema.add("""
                     {
                       "type": ["object"]
                     }
                     """);
    structSchema.add("""
                     {
                       "type": ["null", "object"]
                     }
                     """);

    final AirbyteType struct = new Struct(new LinkedHashMap<>());
    for (final String schema : structSchema) {
      assertEquals(struct, AirbyteType.fromJsonSchema(Jsons.deserialize(schema)));
    }
  }

  @Test
  public void testImplicitStruct() {
    final String structSchema = """
                                {
                                  "properties": {
                                    "key1": {
                                      "type": "boolean"
                                    }
                                  }
                                }
                                """;

    final LinkedHashMap<String, AirbyteType> propertiesMap = new LinkedHashMap<>();
    propertiesMap.put("key1", AirbyteProtocolType.BOOLEAN);

    final AirbyteType struct = new Struct(propertiesMap);
    assertEquals(struct, AirbyteType.fromJsonSchema(Jsons.deserialize(structSchema)));
  }

  @Test
  public void testArray() {
    final List<String> arraySchema = new ArrayList<>();
    arraySchema.add("""
                    {
                      "type": "array",
                      "items": {
                        "type": "string",
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                      }
                    }
                    """);
    arraySchema.add("""
                    {
                      "type": ["array"],
                      "items": {
                        "type": ["string"],
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                      }
                    }
                    """);
    arraySchema.add("""
                    {
                      "type": ["null", "array"],
                      "items": {
                        "type": ["null", "string"],
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                      }
                    }
                    """);

    final AirbyteType array = new Array(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    for (final String schema : arraySchema) {
      assertEquals(array, AirbyteType.fromJsonSchema(Jsons.deserialize(schema)));
    }
  }

  @Test
  public void testEmptyArray() {
    final List<String> arraySchema = new ArrayList<>();
    arraySchema.add("""
                    {
                      "type": "array"
                    }
                    """);
    arraySchema.add("""
                    {
                      "type": ["array"]
                    }
                    """);

    arraySchema.add("""
                    {
                      "type": ["null", "array"]
                    }
                    """);

    final AirbyteType array = new Array(AirbyteProtocolType.UNKNOWN);
    for (final String schema : arraySchema) {
      assertEquals(array, AirbyteType.fromJsonSchema(Jsons.deserialize(schema)));
    }
  }

  @Test
  public void testUnsupportedOneOf() {
    final String unsupportedOneOfSchema = """
                                          {
                                            "oneOf": ["number", "string"]
                                          }
                                          """;

    final List<AirbyteType> options = new ArrayList<>();
    options.add(AirbyteProtocolType.NUMBER);
    options.add(AirbyteProtocolType.STRING);

    final UnsupportedOneOf unsupportedOneOf = new UnsupportedOneOf(options);
    assertEquals(unsupportedOneOf, AirbyteType.fromJsonSchema(Jsons.deserialize(unsupportedOneOfSchema)));
  }

  @Test
  public void testOneOf() {

    final String oneOfSchema = """
                               {
                                 "type": ["string", "number"]
                               }
                               """;

    final List<AirbyteType> options = new ArrayList<>();
    options.add(AirbyteProtocolType.STRING);
    options.add(AirbyteProtocolType.NUMBER);

    final OneOf oneOf = new OneOf(options);
    assertEquals(oneOf, AirbyteType.fromJsonSchema(Jsons.deserialize(oneOfSchema)));
  }

  @Test
  public void testOneOfComplex() {
    JsonNode schema = Jsons.deserialize("""
                                        {
                                          "type": ["string", "object", "array", "null", "string", "object", "array", "null"],
                                          "properties": {
                                            "foo": {"type": "string"}
                                          },
                                          "items": {"type": "string"}
                                        }
                                        """);

    AirbyteType parsed = AirbyteType.fromJsonSchema(schema);

    AirbyteType expected = new OneOf(List.of(
        AirbyteProtocolType.STRING,
        new Struct(new LinkedHashMap<>() {

          {
            put("foo", AirbyteProtocolType.STRING);
          }

        }),
        new Array(AirbyteProtocolType.STRING)));
    assertEquals(expected, parsed);
  }

  @Test
  public void testOneOfUnderspecifiedNonPrimitives() {
    JsonNode schema = Jsons.deserialize("""
                                        {
                                          "type": ["string", "object", "array", "null", "string", "object", "array", "null"]
                                        }
                                        """);

    AirbyteType parsed = AirbyteType.fromJsonSchema(schema);

    AirbyteType expected = new OneOf(List.of(
        AirbyteProtocolType.STRING,
        new Struct(new LinkedHashMap<>()),
        new Array(AirbyteProtocolType.UNKNOWN)));
    assertEquals(expected, parsed);
  }

  @Test
  public void testInvalidTextualType() {
    final String invalidTypeSchema = """
                                     {
                                       "type": "foo"
                                     }
                                     """;
    assertEquals(AirbyteProtocolType.UNKNOWN, AirbyteType.fromJsonSchema(Jsons.deserialize(invalidTypeSchema)));
  }

  @Test
  public void testInvalidBooleanType() {
    final String invalidTypeSchema = """
                                     {
                                       "type": true
                                     }
                                     """;
    assertEquals(AirbyteProtocolType.UNKNOWN, AirbyteType.fromJsonSchema(Jsons.deserialize(invalidTypeSchema)));
  }

  @Test
  public void testInvalid() {
    final List<String> invalidSchema = new ArrayList<>();
    invalidSchema.add("");
    invalidSchema.add("null");
    invalidSchema.add("true");
    invalidSchema.add("false");
    invalidSchema.add("1");
    invalidSchema.add("\"\"");
    invalidSchema.add("[]");
    invalidSchema.add("{}");

    for (final String schema : invalidSchema) {
      assertEquals(AirbyteProtocolType.UNKNOWN, AirbyteType.fromJsonSchema(Jsons.deserialize(schema)));
    }
  }

  @Test
  public void testChooseOneOf() {
    // test ordering

    OneOf o = new OneOf(ImmutableList.of(AirbyteProtocolType.STRING, AirbyteProtocolType.DATE));
    assertEquals(AirbyteProtocolType.DATE, AirbyteTypeUtils.chooseOneOfType(o));

    final Array a = new Array(AirbyteProtocolType.TIME_WITH_TIMEZONE);
    o = new OneOf(ImmutableList.of(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE, a));
    assertEquals(a, AirbyteTypeUtils.chooseOneOfType(o));

    final LinkedHashMap<String, AirbyteType> properties = new LinkedHashMap<>();
    properties.put("key1", AirbyteProtocolType.UNKNOWN);
    properties.put("key2", AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    final Struct s = new Struct(properties);
    o = new OneOf(ImmutableList.of(AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE, s));
    assertEquals(s, AirbyteTypeUtils.chooseOneOfType(o));

    // test exclusion

    o = new OneOf(ImmutableList.of(AirbyteProtocolType.BOOLEAN, AirbyteProtocolType.INTEGER));
    assertEquals(AirbyteProtocolType.INTEGER, AirbyteTypeUtils.chooseOneOfType(o));

    o = new OneOf(ImmutableList.of(AirbyteProtocolType.INTEGER, AirbyteProtocolType.NUMBER, AirbyteProtocolType.DATE));
    assertEquals(AirbyteProtocolType.NUMBER, AirbyteTypeUtils.chooseOneOfType(o));

    o = new OneOf(ImmutableList.of(AirbyteProtocolType.BOOLEAN, AirbyteProtocolType.NUMBER, AirbyteProtocolType.STRING));
    assertEquals(AirbyteProtocolType.STRING, AirbyteTypeUtils.chooseOneOfType(o));
  }

  @Test
  public void testAsColumns() {
    OneOf o = new OneOf(List.of(
        AirbyteProtocolType.STRING,
        new Struct(new LinkedHashMap<>() {

          {
            put("foo", AirbyteProtocolType.STRING);
          }

        }),
        new Array(AirbyteProtocolType.STRING),
        // This is bad behavior, but it matches current behavior so we'll test it.
        // Ideally, we would recognize that the sub-oneOfs are also objects.
        new OneOf(List.of(new Struct(new LinkedHashMap<>()))),
        new UnsupportedOneOf(List.of(new Struct(new LinkedHashMap<>())))));

    LinkedHashMap<String, AirbyteType> columns = o.asColumns();

    assertEquals(
        new LinkedHashMap<>() {

          {
            put("foo", AirbyteProtocolType.STRING);
          }

        },
        columns);
  }

  @Test
  public void testAsColumnsMultipleObjects() {
    OneOf o = new OneOf(List.of(
        new Struct(new LinkedHashMap<>()),
        new Struct(new LinkedHashMap<>())));

    // This prooobably should throw an exception, but for the sake of smooth rollout it just logs a
    // warning for now.
    assertEquals(new LinkedHashMap<>(), o.asColumns());
  }

  @Test
  public void testAsColumnsNoObjects() {
    OneOf o = new OneOf(List.of(
        AirbyteProtocolType.STRING,
        new Array(AirbyteProtocolType.STRING),
        new UnsupportedOneOf(new ArrayList<>()),
        // Similar to testAsColumns(), this is bad behavior.
        new OneOf(List.of(new Struct(new LinkedHashMap<>()))),
        new UnsupportedOneOf(List.of(new Struct(new LinkedHashMap<>())))));

    // This prooobably should throw an exception, but for the sake of smooth rollout it just logs a
    // warning for now.
    assertEquals(new LinkedHashMap<>(), o.asColumns());
  }

}
