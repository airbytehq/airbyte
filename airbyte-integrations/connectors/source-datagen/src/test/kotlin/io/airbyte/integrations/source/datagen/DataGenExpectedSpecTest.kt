/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DataGenExpectedSpecTest {
    @Test
    fun testCopiedMysqlCdcDocumentationLinkReferencesMysqlDocs() {
        val expectedSpec =
            requireNotNull(javaClass.classLoader.getResourceAsStream("expected-spec.json")).use {
                String(it.readAllBytes(), StandardCharsets.UTF_8)
            }

        assertTrue(
            expectedSpec.contains(
                "https://docs.airbyte.com/integrations/sources/mysql/#change-data-capture-cdc"
            )
        )
        assertFalse(expectedSpec.contains("/integrations/sources/mssql/"))
    }
}
