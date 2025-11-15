/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

import java.io.IOException
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class ConfigSchemaTest {
    @Test
    @Throws(IOException::class)
    fun testFile() {
        val schema =
            Files.readString(ConfigSchema.STATE.configSchemaFile.toPath(), StandardCharsets.UTF_8)
        Assertions.assertTrue(schema.contains("title"))
    }

    @Test
    fun testPrepareKnownSchemas() {
        for (value in ConfigSchema.entries) {
            Assertions.assertTrue(
                Files.exists(value.configSchemaFile.toPath()),
                value.configSchemaFile.toPath().toString() + " does not exist"
            )
        }
    }
}
