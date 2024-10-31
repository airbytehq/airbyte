/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class SnowflakeSqlNameTransformerTest {
    @Test
    fun testGetIdentifier() {
        RAW_TO_NORMALIZED_IDENTIFIERS.forEach { (raw: String?, normalized: String?) ->
            Assertions.assertEquals(normalized, INSTANCE.convertStreamName(raw))
            Assertions.assertEquals(normalized, INSTANCE.getIdentifier(raw))
            Assertions.assertEquals(normalized, INSTANCE.getNamespace(raw))
        }
    }

    companion object {
        private val INSTANCE = SnowflakeSQLNameTransformer()
        private val RAW_TO_NORMALIZED_IDENTIFIERS: Map<String, String> =
            java.util.Map.of(
                "name-space",
                "name_space",
                "spécial_character",
                "special_character",
                "99namespace",
                "_99namespace"
            )
    }
}
