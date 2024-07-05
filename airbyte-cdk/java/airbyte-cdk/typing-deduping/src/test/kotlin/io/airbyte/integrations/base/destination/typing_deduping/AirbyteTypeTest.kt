/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Companion.fromJsonSchema
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable

class AirbyteTypeTest {
    @Test
    fun testStruct() {
        val structSchema: MutableList<String> = ArrayList()
        structSchema.add(
            """
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
                           "airbyte_type": "time_without_timezone"
                         },
                         "key7": {
                           "type": "string",
                           "format": "time",
                           "airbyte_type": "time_with_timezone"
                         },
                         "key8": {
                           "type": "string",
                           "format": "date-time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key9": {
                           "type": "string",
                           "format": "date-time",
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
                     
                     """.trimIndent()
        )
        structSchema.add(
            """
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
                           "airbyte_type": "time_without_timezone"
                         },
                         "key7": {
                           "type": ["string"],
                           "format": "time",
                           "airbyte_type": "time_with_timezone"
                         },
                         "key8": {
                           "type": ["string"],
                           "format": "date-time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key9": {
                           "type": ["string"],
                           "format": "date-time",
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
                     
                     """.trimIndent()
        )
        structSchema.add(
            """
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
                           "airbyte_type": "time_without_timezone"
                         },
                         "key7": {
                           "type": ["null", "string"],
                           "format": "time",
                           "airbyte_type": "time_with_timezone"
                         },
                         "key8": {
                           "type": ["null", "string"],
                           "format": "date-time",
                           "airbyte_type": "timestamp_without_timezone"
                         },
                         "key9": {
                           "type": ["null", "string"],
                           "format": "date-time",
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
                     
                     """.trimIndent()
        )

        val propertiesMap = LinkedHashMap<String, AirbyteType>()
        propertiesMap["key1"] = AirbyteProtocolType.BOOLEAN
        propertiesMap["key2"] = AirbyteProtocolType.INTEGER
        propertiesMap["key3"] = AirbyteProtocolType.INTEGER
        propertiesMap["key4"] = AirbyteProtocolType.NUMBER
        propertiesMap["key5"] = AirbyteProtocolType.DATE
        propertiesMap["key6"] = AirbyteProtocolType.TIME_WITHOUT_TIMEZONE
        propertiesMap["key7"] = AirbyteProtocolType.TIME_WITH_TIMEZONE
        propertiesMap["key8"] = AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE
        propertiesMap["key9"] = AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        propertiesMap["key10"] = AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        propertiesMap["key11"] = AirbyteProtocolType.STRING

        val struct: AirbyteType = Struct(propertiesMap)
        for (schema in structSchema) {
            Assertions.assertEquals(struct, fromJsonSchema(Jsons.deserialize(schema)))
        }
    }

    @Test
    fun testEmptyStruct() {
        val structSchema: MutableList<String> = ArrayList()
        structSchema.add(
            """
                     {
                       "type": "object"
                     }
                     
                     """.trimIndent()
        )
        structSchema.add(
            """
                     {
                       "type": ["object"]
                     }
                     
                     """.trimIndent()
        )
        structSchema.add(
            """
                     {
                       "type": ["null", "object"]
                     }
                     
                     """.trimIndent()
        )

        val struct: AirbyteType = Struct(LinkedHashMap())
        for (schema in structSchema) {
            Assertions.assertEquals(struct, fromJsonSchema(Jsons.deserialize(schema)))
        }
    }

    @Test
    fun testImplicitStruct() {
        val structSchema =
            """
                                {
                                  "properties": {
                                    "key1": {
                                      "type": "boolean"
                                    }
                                  }
                                }
                                
                                """.trimIndent()

        val propertiesMap = LinkedHashMap<String, AirbyteType>()
        propertiesMap["key1"] = AirbyteProtocolType.BOOLEAN

        val struct: AirbyteType = Struct(propertiesMap)
        Assertions.assertEquals(struct, fromJsonSchema(Jsons.deserialize(structSchema)))
    }

    @Test
    fun testArray() {
        val arraySchema: MutableList<String> = ArrayList()
        arraySchema.add(
            """
                    {
                      "type": "array",
                      "items": {
                        "type": "string",
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                      }
                    }
                    
                    """.trimIndent()
        )
        arraySchema.add(
            """
                    {
                      "type": ["array"],
                      "items": {
                        "type": ["string"],
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                      }
                    }
                    
                    """.trimIndent()
        )
        arraySchema.add(
            """
                    {
                      "type": ["null", "array"],
                      "items": {
                        "type": ["null", "string"],
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                      }
                    }
                    
                    """.trimIndent()
        )

        val array: AirbyteType = Array(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE)
        for (schema in arraySchema) {
            Assertions.assertEquals(array, fromJsonSchema(Jsons.deserialize(schema)))
        }
    }

    @Test
    fun testEmptyArray() {
        val arraySchema: MutableList<String> = ArrayList()
        arraySchema.add(
            """
                    {
                      "type": "array"
                    }
                    
                    """.trimIndent()
        )
        arraySchema.add(
            """
                    {
                      "type": ["array"]
                    }
                    
                    """.trimIndent()
        )

        arraySchema.add(
            """
                    {
                      "type": ["null", "array"]
                    }
                    
                    """.trimIndent()
        )

        val array: AirbyteType = Array(AirbyteProtocolType.UNKNOWN)
        for (schema in arraySchema) {
            Assertions.assertEquals(array, fromJsonSchema(Jsons.deserialize(schema)))
        }
    }

    @Test
    fun testUnsupportedOneOf() {
        val unsupportedOneOfSchema =
            """
                                          {
                                            "oneOf": ["number", "string"]
                                          }
                                          
                                          """.trimIndent()

        val options: MutableList<AirbyteType> = ArrayList()
        options.add(AirbyteProtocolType.NUMBER)
        options.add(AirbyteProtocolType.STRING)

        val unsupportedOneOf = UnsupportedOneOf(options)
        Assertions.assertEquals(
            unsupportedOneOf,
            fromJsonSchema(Jsons.deserialize(unsupportedOneOfSchema))
        )
    }

    @Test
    fun testUnion() {
        val unionSchema =
            """
                               {
                                 "type": ["string", "number"]
                               }
                               
                               """.trimIndent()

        val options: MutableList<AirbyteType> = ArrayList()
        options.add(AirbyteProtocolType.STRING)
        options.add(AirbyteProtocolType.NUMBER)

        val union = Union(options)
        Assertions.assertEquals(union, fromJsonSchema(Jsons.deserialize(unionSchema)))
    }

    @Test
    fun testUnionComplex() {
        val schema =
            Jsons.deserialize(
                """
                                              {
                                                "type": ["string", "object", "array", "null", "string", "object", "array", "null"],
                                                "properties": {
                                                  "foo": {"type": "string"}
                                                },
                                                "items": {"type": "string"}
                                              }
                                              
                                              """.trimIndent()
            )

        val parsed = fromJsonSchema(schema)

        val expected: AirbyteType =
            Union(
                List.of(
                    AirbyteProtocolType.STRING,
                    Struct(linkedMapOf("foo" to AirbyteProtocolType.STRING)),
                    Array(AirbyteProtocolType.STRING)
                )
            )
        Assertions.assertEquals(expected, parsed)
    }

    @Test
    fun testUnionUnderspecifiedNonPrimitives() {
        val schema =
            Jsons.deserialize(
                """
                                              {
                                                "type": ["string", "object", "array", "null", "string", "object", "array", "null"]
                                              }
                                              
                                              """.trimIndent()
            )

        val parsed = fromJsonSchema(schema)

        val expected: AirbyteType =
            Union(
                List.of(
                    AirbyteProtocolType.STRING,
                    Struct(LinkedHashMap()),
                    Array(AirbyteProtocolType.UNKNOWN)
                )
            )
        expected.toString()
        Assertions.assertEquals(expected, parsed)
    }

    @Test
    fun testInvalidTextualType() {
        val invalidTypeSchema =
            """
                                     {
                                       "type": "foo"
                                     }
                                     
                                     """.trimIndent()
        Assertions.assertEquals(
            AirbyteProtocolType.UNKNOWN,
            fromJsonSchema(Jsons.deserialize(invalidTypeSchema))
        )
    }

    @Test
    fun testInvalidBooleanType() {
        val invalidTypeSchema =
            """
                                     {
                                       "type": true
                                     }
                                     
                                     """.trimIndent()
        Assertions.assertEquals(
            AirbyteProtocolType.UNKNOWN,
            fromJsonSchema(Jsons.deserialize(invalidTypeSchema))
        )
    }

    @Test
    fun testInvalid() {
        val invalidSchema: MutableList<String> = ArrayList()
        invalidSchema.add("")
        invalidSchema.add("null")
        invalidSchema.add("true")
        invalidSchema.add("false")
        invalidSchema.add("1")
        invalidSchema.add("\"\"")
        invalidSchema.add("[]")
        invalidSchema.add("{}")

        for (schema in invalidSchema) {
            Assertions.assertEquals(
                AirbyteProtocolType.UNKNOWN,
                fromJsonSchema(Jsons.deserialize(schema))
            )
        }
    }

    @Test
    fun testChooseUnion() {
        val unionToType: MutableMap<Union, AirbyteType> = HashMap()

        val a = Array(AirbyteProtocolType.BOOLEAN)

        val properties = LinkedHashMap<String, AirbyteType>()
        properties["key1"] = AirbyteProtocolType.UNKNOWN
        properties["key2"] = AirbyteProtocolType.INTEGER
        val s = Struct(properties)

        unionToType[Union(listOf(s, a))] = a
        unionToType[Union(listOf(AirbyteProtocolType.NUMBER, a))] = a
        unionToType[Union(listOf(AirbyteProtocolType.INTEGER, s))] = s
        unionToType[
            Union(
                listOf(
                    AirbyteProtocolType.NUMBER,
                    AirbyteProtocolType.DATE,
                    AirbyteProtocolType.BOOLEAN
                )
            )
        ] = AirbyteProtocolType.DATE
        unionToType[
            Union(
                listOf(
                    AirbyteProtocolType.INTEGER,
                    AirbyteProtocolType.BOOLEAN,
                    AirbyteProtocolType.NUMBER
                )
            )
        ] = AirbyteProtocolType.NUMBER
        unionToType[Union(listOf(AirbyteProtocolType.BOOLEAN, AirbyteProtocolType.INTEGER))] =
            AirbyteProtocolType.INTEGER

        Assertions.assertAll(
            unionToType.entries.map { e ->
                Executable { Assertions.assertEquals(e.value, e.key.chooseType()) }
            }
        )
    }

    @Test
    fun testAsColumns() {
        val u =
            Union(
                List.of(
                    AirbyteProtocolType.STRING,
                    Struct(linkedMapOf("foo" to AirbyteProtocolType.STRING)),
                    Array(
                        AirbyteProtocolType.STRING
                    ), // This is bad behavior, but it matches current behavior so we'll test it.
                    // Ideally, we would recognize that the sub-unions are also objects.
                    Union(List.of(Struct(LinkedHashMap()))),
                    UnsupportedOneOf(List.of(Struct(LinkedHashMap())))
                )
            )

        val columns = u.asColumns()

        Assertions.assertEquals(
            object : LinkedHashMap<Any?, Any?>() {
                init {
                    put("foo", AirbyteProtocolType.STRING)
                }
            },
            columns
        )
    }

    @Test
    fun testAsColumnsMultipleObjects() {
        val u = Union(List.of(Struct(LinkedHashMap()), Struct(LinkedHashMap())))

        // This prooobably should throw an exception, but for the sake of smooth rollout it just
        // logs a
        // warning for now.
        Assertions.assertEquals(LinkedHashMap<Any, Any>(), u.asColumns())
    }

    @Test
    fun testAsColumnsNoObjects() {
        val u =
            Union(
                List.of(
                    AirbyteProtocolType.STRING,
                    Array(AirbyteProtocolType.STRING),
                    UnsupportedOneOf(
                        ArrayList()
                    ), // Similar to testAsColumns(), this is bad behavior.
                    Union(List.of(Struct(LinkedHashMap()))),
                    UnsupportedOneOf(List.of(Struct(LinkedHashMap())))
                )
            )

        // This prooobably should throw an exception, but for the sake of smooth rollout it just
        // logs a
        // warning for now.
        Assertions.assertEquals(LinkedHashMap<Any, Any>(), u.asColumns())
    }
}
