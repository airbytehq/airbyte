/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

import io.airbyte.cdk.load.command.DestinationStream
import org.apache.iceberg.catalog.Namespace
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class TableIdGeneratorTest {

    @Test
    fun `tableIdOf with single-level namespace`() {
        val tableId = tableIdOf("my_namespace", "my_table")
        assertThat(tableId.namespace()).isEqualTo(Namespace.of("my_namespace"))
        assertThat(tableId.namespace().levels()).hasSize(1)
        assertThat(tableId.name()).isEqualTo("my_table")
    }

    @Test
    fun `tableIdOf with dotted namespace creates multi-level namespace`() {
        val tableId = tableIdOf("a.b.c", "my_table")
        assertThat(tableId.namespace()).isEqualTo(Namespace.of("a", "b", "c"))
        assertThat(tableId.namespace().levels()).hasSize(3)
        assertThat(tableId.namespace().level(0)).isEqualTo("a")
        assertThat(tableId.namespace().level(1)).isEqualTo("b")
        assertThat(tableId.namespace().level(2)).isEqualTo("c")
        assertThat(tableId.name()).isEqualTo("my_table")
    }

    @Test
    fun `tableIdOf with deeply nested namespace`() {
        val tableId = tableIdOf("operational.lims.inventory.bronze", "events")
        assertThat(tableId.namespace().levels()).hasSize(4)
        assertThat(tableId.namespace())
            .isEqualTo(Namespace.of("operational", "lims", "inventory", "bronze"))
        assertThat(tableId.name()).isEqualTo("events")
    }

    @Test
    fun `SimpleTableIdGenerator uses stream namespace when present`() {
        val generator = SimpleTableIdGenerator("default_ns")
        val descriptor = DestinationStream.Descriptor(namespace = "custom_ns", name = "my_table")
        val tableId = generator.toTableIdentifier(descriptor)
        assertThat(tableId.namespace()).isEqualTo(Namespace.of("custom_ns"))
        assertThat(tableId.name()).isEqualTo("my_table")
    }

    @Test
    fun `SimpleTableIdGenerator falls back to config namespace`() {
        val generator = SimpleTableIdGenerator("fallback_ns")
        val descriptor = DestinationStream.Descriptor(namespace = null, name = "my_table")
        val tableId = generator.toTableIdentifier(descriptor)
        assertThat(tableId.namespace()).isEqualTo(Namespace.of("fallback_ns"))
        assertThat(tableId.name()).isEqualTo("my_table")
    }

    @Test
    fun `SimpleTableIdGenerator handles dotted stream namespace`() {
        val generator = SimpleTableIdGenerator("default")
        val descriptor =
            DestinationStream.Descriptor(namespace = "org.dept.team", name = "my_table")
        val tableId = generator.toTableIdentifier(descriptor)
        assertThat(tableId.namespace()).isEqualTo(Namespace.of("org", "dept", "team"))
        assertThat(tableId.namespace().levels()).hasSize(3)
    }

    @Test
    fun `SimpleTableIdGenerator handles dotted config namespace`() {
        val generator = SimpleTableIdGenerator("org.dept.team")
        val descriptor = DestinationStream.Descriptor(namespace = null, name = "my_table")
        val tableId = generator.toTableIdentifier(descriptor)
        assertThat(tableId.namespace()).isEqualTo(Namespace.of("org", "dept", "team"))
        assertThat(tableId.namespace().levels()).hasSize(3)
    }
}
