/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.io.IOs.writeFile
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.validation.json.JsonSchemaValidator
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/**
 * Tests that the Redshift spec passes JsonSchema validation. While this may seem like overkill, we
 * are doing it because there are some gotchas in correctly configuring the oneOf.
 */
class RedshiftSpecTest {
    @BeforeEach
    fun beforeEach() {
        config = deserialize(configText)
    }

    @Test
    fun testHostMissing() {
        (config as ObjectNode?)!!.remove("host")
        Assertions.assertFalse(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testPortMissing() {
        (config as ObjectNode?)!!.remove("port")
        Assertions.assertFalse(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testDatabaseMissing() {
        (config as ObjectNode?)!!.remove("database")
        Assertions.assertFalse(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testUsernameMissing() {
        (config as ObjectNode?)!!.remove("username")
        Assertions.assertFalse(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testPasswordMissing() {
        (config as ObjectNode?)!!.remove("password")
        Assertions.assertFalse(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testSchemaMissing() {
        (config as ObjectNode?)!!.remove("schema")
        Assertions.assertFalse(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testAdditionalJdbcParamMissing() {
        (config as ObjectNode?)!!.remove("jdbc_url_params")
        Assertions.assertTrue(validator!!.test(schema!!, config!!))
    }

    @Test
    fun testWithJdbcAdditionalProperty() {
        Assertions.assertTrue(validator!!.test(schema!!, config!!))
    }

    @Test
    @Throws(Exception::class)
    fun testJdbcAdditionalProperty() {
        val spec = RedshiftDestination().spec()
        Assertions.assertNotNull(spec.connectionSpecification["properties"]["jdbc_url_params"])
    }

    companion object {
        private var schema: JsonNode? = null
        private var config: JsonNode? = null
        private var configText: String? = null
        private var validator: JsonSchemaValidator? = null

        @JvmStatic
        @BeforeAll
        @Throws(IOException::class)
        fun init() {
            configText = readResource("config-test.json")
            val spec = readResource("spec.json")
            val schemaFile =
                writeFile(
                        Files.createTempDirectory(Path.of("/tmp"), "spec-test"),
                        "schema.json",
                        spec
                    )
                    .toFile()
            schema = JsonSchemaValidator.getSchema(schemaFile).get("connectionSpecification")
            validator = JsonSchemaValidator()
        }
    }
}
