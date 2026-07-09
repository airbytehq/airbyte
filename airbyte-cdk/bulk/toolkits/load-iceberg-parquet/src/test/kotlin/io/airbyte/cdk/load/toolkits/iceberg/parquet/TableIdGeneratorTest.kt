/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class TableIdGeneratorTest {

    @Test
    fun `single-level namespace maps to one level`() {
        val id = tableIdOf("myschema", "mytable")
        assertEquals(listOf("myschema"), id.namespace().levels().toList())
        assertEquals("mytable", id.name())
    }

    @Test
    fun `dotted namespace maps to multiple levels`() {
        val id = tableIdOf("operational.lims.inventory.bronze", "container")
        assertEquals(
            listOf("operational", "lims", "inventory", "bronze"),
            id.namespace().levels().toList(),
        )
        assertEquals("container", id.name())
    }
}
