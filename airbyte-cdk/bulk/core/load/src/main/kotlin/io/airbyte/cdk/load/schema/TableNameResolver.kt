/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

/** Applies destination-specific table name munging logic and handles any naming collisions. */
@Singleton
class TableNameResolver(
    private val mapper: TableSchemaMapper,
) {
    private val log = KotlinLogging.logger {}

    fun getTableNameMapping(
        streamDescriptors: Set<DestinationStream.Descriptor>,
    ): Map<DestinationStream.Descriptor, TableName> {
        val processedFinalTableNames = mutableSetOf<TableName>()

        val result = mutableMapOf<DestinationStream.Descriptor, TableName>()

        streamDescriptors.forEach { desc ->
            val originalFinalTableName = mapper.toFinalTableName(desc)
            val currentFinalProcessedName: TableName

            val finalTableNameColliding = originalFinalTableName in processedFinalTableNames
            if (finalTableNameColliding) {
                log.info { "Detected table name collision for ${desc.namespace}.${desc.name}" }
                // Create a hash-suffixed name to avoid collision
                val hash =
                    DigestUtils.sha1Hex(
                            "${originalFinalTableName.namespace}&airbyte&${desc.name}",
                        )
                        .substring(0, 3)
                val newName = "${desc.name}_$hash"

                currentFinalProcessedName =
                    mapper.toFinalTableName(
                        desc.copy(name = newName),
                    )
                processedFinalTableNames.add(currentFinalProcessedName)
            } else {
                processedFinalTableNames.add(originalFinalTableName)
                currentFinalProcessedName = originalFinalTableName
            }

            result[desc] = currentFinalProcessedName
        }

        return result
    }
}
