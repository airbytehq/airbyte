/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

import jakarta.inject.Singleton
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.SupportsPrefixOperations

@Singleton
class IcebergTableCleaner {

    fun clearTable(
        catalog: Catalog,
        identifier: TableIdentifier,
        io: FileIO,
        tableLocation: String
    ) {
        catalog.dropTable(identifier, true)
        if (io is SupportsPrefixOperations) {
            io.deletePrefix(tableLocation)
        }
    }
}
