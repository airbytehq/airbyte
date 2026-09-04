/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class DatabricksOffsetDateTimeFieldTypeTest {

    private val fieldType = DatabricksOffsetDateTimeFieldType

    @Test
    fun testSchemaType() {
        // Test that the field type has the correct schema type
        assertEquals(
            io.airbyte.cdk.data.LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            fieldType.airbyteSchemaType
        )
    }

    @Test
    fun testFieldTypeExists() {
        // Test that the field type is properly instantiated
        assertEquals(DatabricksOffsetDateTimeFieldType, fieldType)
    }
}
