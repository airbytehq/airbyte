/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.SupportsNamespaces
import org.junit.jupiter.api.Test

/** Combined Catalog + SupportsNamespaces interface for mocking. */
private interface NamespaceCatalog : org.apache.iceberg.catalog.Catalog, SupportsNamespaces

class IcebergUtilCreateNamespaceTest {

    private val coercer = mockk<AirbyteValueCoercer>()

    @Test
    fun `createNamespace creates single-level namespace`() {
        val generator = SimpleTableIdGenerator("default")
        val util = IcebergUtil(generator, coercer)
        val catalog = mockk<NamespaceCatalog>()
        val ns = Namespace.of("my_db")

        every { catalog.namespaceExists(ns) } returns false
        every { catalog.createNamespace(ns) } just runs

        val descriptor = DestinationStream.Descriptor(namespace = "my_db", name = "table")
        util.createNamespace(descriptor, catalog)

        verify(exactly = 1) { catalog.createNamespace(ns) }
    }

    @Test
    fun `createNamespace creates parent namespaces before leaf for multi-level`() {
        val generator = SimpleTableIdGenerator("default")
        val util = IcebergUtil(generator, coercer)
        val catalog = mockk<NamespaceCatalog>()

        val nsA = Namespace.of("a")
        val nsAB = Namespace.of("a", "b")
        val nsABC = Namespace.of("a", "b", "c")

        every { catalog.namespaceExists(nsA) } returns false
        every { catalog.namespaceExists(nsAB) } returns false
        every { catalog.namespaceExists(nsABC) } returns false
        every { catalog.createNamespace(nsA) } just runs
        every { catalog.createNamespace(nsAB) } just runs
        every { catalog.createNamespace(nsABC) } just runs

        val descriptor = DestinationStream.Descriptor(namespace = "a.b.c", name = "table")
        util.createNamespace(descriptor, catalog)

        verify(exactly = 1) { catalog.createNamespace(nsA) }
        verify(exactly = 1) { catalog.createNamespace(nsAB) }
        verify(exactly = 1) { catalog.createNamespace(nsABC) }
    }

    @Test
    fun `createNamespace skips existing parent namespaces`() {
        val generator = SimpleTableIdGenerator("default")
        val util = IcebergUtil(generator, coercer)
        val catalog = mockk<NamespaceCatalog>()

        val nsA = Namespace.of("a")
        val nsAB = Namespace.of("a", "b")

        // parent "a" already exists
        every { catalog.namespaceExists(nsA) } returns true
        every { catalog.namespaceExists(nsAB) } returns false
        every { catalog.createNamespace(nsAB) } just runs

        val descriptor = DestinationStream.Descriptor(namespace = "a.b", name = "table")
        util.createNamespace(descriptor, catalog)

        verify(exactly = 0) { catalog.createNamespace(nsA) }
        verify(exactly = 1) { catalog.createNamespace(nsAB) }
    }
}
