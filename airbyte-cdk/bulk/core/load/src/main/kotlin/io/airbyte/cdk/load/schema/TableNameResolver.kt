package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import jakarta.inject.Singleton

@Singleton
class TableNameResolver(
    private val mapper: TableSchemaMapper,
    private val ignoreCaseColNames: Boolean,
) {
    fun cat() {
     val processedFinalTableNames = mutableSetOf<TableName>()

        val result = mutableMapOf<DestinationStream, TableName>()

        catalog.streams.forEach { stream ->
            val originalRawTableName = rawTableNameGenerator?.getTableName(stream.mappedDescriptor)
            val originalFinalTableName =
                finalTableNameGenerator.getTableName(stream.mappedDescriptor)
            val currentRawProcessedName: TableName?
            val currentFinalProcessedName: TableName

            val rawTableNameColliding =
                processedRawTableNames?.let { originalRawTableName contains it } ?: false
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
}
