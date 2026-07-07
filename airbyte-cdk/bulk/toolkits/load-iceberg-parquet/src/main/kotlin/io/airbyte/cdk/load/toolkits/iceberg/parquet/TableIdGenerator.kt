/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

import io.airbyte.cdk.load.command.DestinationStream
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier

/**
 * Convert our internal stream descriptor to an Iceberg [TableIdentifier]. Implementations should
 * handle catalog-specific naming restrictions.
 */
// TODO accept default namespace in config as a val here
interface TableIdGenerator {
    fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier
}

class SimpleTableIdGenerator(private val configNamespace: String? = "") : TableIdGenerator {
    override fun toTableIdentifier(stream: DestinationStream.Descriptor): TableIdentifier {
        val namespace = stream.namespace ?: configNamespace
        return tableIdOf(namespace!!, stream.name)
    }
}

// iceberg namespace+name must both be nonnull.
// A dotted namespace (e.g. "operational.lims.inventory.bronze") is a multi-level
// Iceberg namespace; split it so each dot-segment becomes its own level. REST
// catalogs (Lakekeeper, Polaris) reject a single namespace part containing '.'.
// A dotless name splits to a one-element array, so single-level names are
// unaffected.
fun tableIdOf(namespace: String, name: String): TableIdentifier =
    TableIdentifier.of(Namespace.of(*namespace.split(".").toTypedArray()), name)
