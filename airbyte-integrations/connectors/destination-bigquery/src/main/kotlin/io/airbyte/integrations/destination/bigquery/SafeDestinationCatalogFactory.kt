/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DefaultDestinationCatalogFactory
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.config.CHECK_STREAM_NAMESPACE
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import org.apache.commons.lang3.RandomStringUtils

@Factory
@Replaces(DefaultDestinationCatalogFactory::class)
class SafeDestinationCatalogFactory {
    @Singleton
    fun getDestinationCatalog(
        catalog: ConfiguredAirbyteCatalog,
        namespaceMapper: NamespaceMapper,
        jsonSchemaToAirbyteType: JsonSchemaToAirbyteType,
        @Value("\${${Operation.PROPERTY}}") operation: String,
        @Named("checkNamespace") checkNamespace: String?,
    ): DestinationCatalog {
        if (operation == "check") {
             // Copied from DefaultDestinationCatalogFactory to maintain behavior
             val date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"))
             val random = RandomStringUtils.randomAlphabetic(5).lowercase()
             val namespace = checkNamespace ?: "${CHECK_STREAM_NAMESPACE}_$date$random"
             return DestinationCatalog(
                 listOf(
                     DestinationStream(
                         unmappedNamespace = namespace,
                         unmappedName = "test$date$random",
                         importType = Append,
                         schema =
                             ObjectType(
                                 linkedMapOf("test" to FieldType(IntegerType, nullable = true))
                             ),
                         generationId = 1,
                         minimumGenerationId = 0,
                         syncId = 1,
                         namespaceMapper = namespaceMapper
                     )
                 )
             )
        } else {
            val streams =
                catalog.streams.map { stream ->
                    val importType =
                        when (stream.destinationSyncMode) {
                            null -> throw IllegalArgumentException("Destination sync mode was null")
                            DestinationSyncMode.OVERWRITE -> Overwrite
                            DestinationSyncMode.APPEND -> Append
                            DestinationSyncMode.APPEND_DEDUP ->
                                Dedupe(
                                    primaryKey = stream.primaryKey ?: emptyList(),
                                    cursor = stream.cursorField ?: emptyList()
                                )
                            DestinationSyncMode.UPDATE -> Update
                            DestinationSyncMode.SOFT_DELETE -> SoftDelete
                        }

                    DestinationStream(
                        unmappedName = stream.stream.name,
                        unmappedNamespace = stream.stream.namespace,
                        importType = importType,
                        schema = jsonSchemaToAirbyteType.convert(stream.stream.jsonSchema),
                        generationId = stream.generationId ?: 0,
                        minimumGenerationId = stream.minimumGenerationId ?: 0,
                        syncId = stream.syncId ?: 0,
                        namespaceMapper = namespaceMapper,
                    )
                }
            return DestinationCatalog(streams)
        }
    }
}
