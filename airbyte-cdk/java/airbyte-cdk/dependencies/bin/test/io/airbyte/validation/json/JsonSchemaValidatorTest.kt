/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.validation.json

import com.fasterxml.jackson.databind.JsonNode
import com.networknt.schema.SchemaLocation
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import java.io.IOException
import java.net.URISyntaxException
import java.nio.file.Files
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class JsonSchemaValidatorTest {
    @Test
    fun testValidateSuccess() {
        val validator = JsonSchemaValidator()

        val object1 = Jsons.deserialize("{\"host\":\"abc\"}")
        Assertions.assertTrue(validator.validate(VALID_SCHEMA, object1).isEmpty())
        Assertions.assertDoesNotThrow { validator.ensure(VALID_SCHEMA, object1) }

        val object2 = Jsons.deserialize("{\"host\":\"abc\", \"port\":1}")
        Assertions.assertTrue(validator.validate(VALID_SCHEMA, object2).isEmpty())
        Assertions.assertDoesNotThrow { validator.ensure(VALID_SCHEMA, object2) }
    }

    @Test
    fun testValidateFail() {
        val validator = JsonSchemaValidator()

        val object1 = Jsons.deserialize("{}")
        Assertions.assertFalse(validator.validate(VALID_SCHEMA, object1).isEmpty())
        Assertions.assertThrows(JsonValidationException::class.java) {
            validator.ensure(VALID_SCHEMA, object1)
        }

        val object2 = Jsons.deserialize("{\"host\":\"abc\", \"port\":9999999}")
        Assertions.assertFalse(validator.validate(VALID_SCHEMA, object2).isEmpty())
        Assertions.assertThrows(JsonValidationException::class.java) {
            validator.ensure(VALID_SCHEMA, object2)
        }
    }

    @Test
    @Throws(IOException::class)
    fun test() {
        val schema =
            """{
  "${"$"}schema": "http://json-schema.org/draft-07/schema#",
  "title": "OuterObject",
  "type": "object",
  "properties": {
    "field1": {
      "type": "string"
    }
  },
  "definitions": {
    "InnerObject": {
      "type": "object",
      "properties": {
        "field2": {
          "type": "string"
        }
      }
    }
  }
}
"""

        val schemaFile =
            IOs.writeFile(Files.createTempDirectory("test"), "schema.json", schema).toFile()

        // outer object
        Assertions.assertTrue(JsonSchemaValidator.getSchema(schemaFile)[PROPERTIES].has("field1"))
        Assertions.assertFalse(JsonSchemaValidator.getSchema(schemaFile)[PROPERTIES].has("field2"))
        // inner object
        Assertions.assertTrue(
            JsonSchemaValidator.getSchema(schemaFile, "InnerObject")[PROPERTIES].has("field2")
        )
        Assertions.assertFalse(
            JsonSchemaValidator.getSchema(schemaFile, "InnerObject")[PROPERTIES].has("field1")
        )
        // non-existent object
        Assertions.assertThrows(NullPointerException::class.java) {
            JsonSchemaValidator.getSchema(schemaFile, "NonExistentObject")
        }
    }

    @Test
    @Throws(IOException::class, URISyntaxException::class)
    fun testResolveReferences() {
        val referencableSchemas =
            """
                                 {
                                   "definitions": {
                                     "ref1": {"type": "string"},
                                     "ref2": {"type": "boolean"}
                                   }
                                 }
                                 
                                 """.trimIndent()
        val schemaFile =
            IOs.writeFile(
                    Files.createTempDirectory("test"),
                    "WellKnownTypes.json",
                    referencableSchemas
                )
                .toFile()
        val jsonSchemaValidator =
            JsonSchemaValidator(
                SchemaLocation.of("file://" + schemaFile.parentFile.absolutePath + "/foo.json")
            )

        val validationResult =
            jsonSchemaValidator.validate(
                Jsons.deserialize(
                    """
                          {
                            "type": "object",
                            "properties": {
                              "prop1": {"${'$'}ref": "WellKnownTypes.json#/definitions/ref1"},
                              "prop2": {"${'$'}ref": "WellKnownTypes.json#/definitions/ref2"}
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "prop1": "foo",
                            "prop2": "false"
                          }
                          
                          """.trimIndent()
                )
            )

        Assertions.assertEquals(setOf("$.prop2: string found, boolean expected"), validationResult)
    }

    @Test
    fun testIntializedMethodsShouldErrorIfNotInitialised() {
        val validator = JsonSchemaValidator()

        Assertions.assertThrows(NullPointerException::class.java) {
            validator.testInitializedSchema("uninitialised", Jsons.deserialize("{}"))
        }
        Assertions.assertThrows(NullPointerException::class.java) {
            validator.ensureInitializedSchema("uninitialised", Jsons.deserialize("{}"))
        }
    }

    @Test
    fun testIntializedMethodsShouldValidateIfInitialised() {
        val validator = JsonSchemaValidator()
        val schemaName = "schema_name"
        val goodJson = Jsons.deserialize("{\"host\":\"abc\"}")

        validator.initializeSchemaValidator(schemaName, VALID_SCHEMA)

        Assertions.assertTrue(validator.testInitializedSchema(schemaName, goodJson))
        Assertions.assertDoesNotThrow { validator.ensureInitializedSchema(schemaName, goodJson) }

        val badJson = Jsons.deserialize("{\"host\":1}")
        Assertions.assertFalse(validator.testInitializedSchema(schemaName, badJson))
        Assertions.assertThrows(JsonValidationException::class.java) {
            validator.ensureInitializedSchema(schemaName, badJson)
        }
    }

    companion object {
        private const val PROPERTIES = "properties"

        private val VALID_SCHEMA: JsonNode =
            Jsons.deserialize(
                """{
    "${"$"}schema": "http://json-schema.org/draft-07/schema#",
    "title": "test",
    "type": "object",
    "required": ["host"],
    "additionalProperties": false,
    "properties": {
      "host": {
        "type": "string"
      },
      "port": {
        "type": "integer",
        "minimum": 0,
        "maximum": 65536
      }    }
  }"""
            )
    }
}
