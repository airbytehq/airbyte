/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.schema.DestinationStream
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

private val LOGGER = KotlinLogging.logger {}
const val DEFAULT_AIRBYTE_INTERNAL_NAMESPACE = "airbyte_internal"

data class TableNameInfo(val tableNames: TableNames)

data class TableCatalog(private val catalog: Map<DestinationStream, TableNameInfo>) :
    Map<DestinationStream, TableNameInfo> by catalog

data class TableCatalogByDescriptor(
    private val catalog: Map<DestinationStream.Descriptor, TableNameInfo>
) : Map<DestinationStream.Descriptor, TableNameInfo> by catalog {
    fun getFinalTableName(desc: DestinationStream.Descriptor): TableName? =
        this[desc]?.tableNames?.finalTableName
}

@Factory
class TableCatalogFactory {
    @Singleton
    fun getTableCatalog(
        catalog: DestinationCatalog,
        // Raw table generator is optional. Direct-load destinations don't need it
        // (unless they were previously T+D destinations, in which case it's still required
        // so that we maintain stable names with the T+D version)
        rawTableNameGenerator: RawTableNameGenerator?,
        finalTableNameGenerator: FinalTableNameGenerator,
    ): TableCatalog {
        val processedRawTableNames =
            if (rawTableNameGenerator != null) {
                mutableSetOf<TableName>()
            } else {
                null
            }
        val processedFinalTableNames = mutableSetOf<TableName>()

        val result = mutableMapOf<DestinationStream, TableNameInfo>()

        catalog.streams.forEach { stream ->
            val originalRawTableName = rawTableNameGenerator?.getTableName(stream.mappedDescriptor)
            val originalFinalTableName =
                finalTableNameGenerator.getTableName(stream.mappedDescriptor)
            val currentRawProcessedName: TableName?
            val currentFinalProcessedName: TableName

            val rawTableNameColliding =
                processedRawTableNames?.let { originalRawTableName in it } ?: false
            val finalTableNameColliding = originalFinalTableName in processedFinalTableNames
            if (rawTableNameColliding || finalTableNameColliding) {
                LOGGER.info {
                    "Detected table name collision for ${stream.mappedDescriptor.namespace}.${stream.mappedDescriptor.name}"
                }
                // Create a hash-suffixed name to avoid collision
                val hash =
                    DigestUtils.sha1Hex(
                            "${originalFinalTableName.namespace}&airbyte&${stream.mappedDescriptor.name}"
                        )
                        .substring(0, 3)
                val newName = "${stream.mappedDescriptor.name}_$hash"

                currentRawProcessedName =
                    rawTableNameGenerator?.getTableName(
                        stream.mappedDescriptor.copy(name = newName)
                    )
                processedRawTableNames?.add(currentRawProcessedName!!)
                currentFinalProcessedName =
                    finalTableNameGenerator.getTableName(
                        stream.mappedDescriptor.copy(name = newName)
                    )
                processedFinalTableNames.add(currentFinalProcessedName)
            } else {
                processedRawTableNames?.add(originalRawTableName!!)
                processedFinalTableNames.add(originalFinalTableName)
                currentRawProcessedName = originalRawTableName
                currentFinalProcessedName = originalFinalTableName
            }

            result[stream] =
                TableNameInfo(
                    TableNames(
                        rawTableName = currentRawProcessedName,
                        finalTableName = currentFinalProcessedName,
                    )
                )
        }

        return TableCatalog(result)
    }

    @Singleton
    fun getTableCatalogByDescriptor(map: TableCatalog): TableCatalogByDescriptor {
        return TableCatalogByDescriptor(map.mapKeys { (k, _) -> k.mappedDescriptor })
    }
}
