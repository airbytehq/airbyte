/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.config.CHECK_STREAM_NAMESPACE
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.schema.TableNameResolver
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import org.apache.commons.lang3.RandomStringUtils

/**
 * Internal representation of destination streams. This is intended to be a case class specialized
 * for usability.
 */
data class DestinationCatalog(val streams: List<DestinationStream> = emptyList()) {
    private val log = KotlinLogging.logger {}

    private val byDescriptor: Map<DestinationStream.Descriptor, DestinationStream> =
        streams.associateBy { it.mappedDescriptor }

    init {
        if (streams.isEmpty()) {
            throw IllegalArgumentException(
                "Catalog must have at least one stream: check that files are in the correct location."
            )
        }

        val duplicateStreamDescriptors =
            streams.groupingBy { it.mappedDescriptor }.eachCount().filter { it.value > 1 }.keys
        if (duplicateStreamDescriptors.isNotEmpty()) {
            throw ConfigErrorException(
                "Some streams appeared multiple times: ${duplicateStreamDescriptors.map { it.toPrettyString() }}"
            )
        }
        throwIfInvalidDedupConfig()

        log.info { "Destination catalog initialized: $streams" }
    }

    fun getStream(name: String, namespace: String?): DestinationStream {
        val descriptor = DestinationStream.Descriptor(namespace = namespace, name = name)
        return byDescriptor[descriptor]
            ?: throw IllegalArgumentException("Stream not found: namespace=$namespace, name=$name")
    }

    fun getStream(descriptor: DestinationStream.Descriptor): DestinationStream {
        return byDescriptor[descriptor]
            ?: throw IllegalArgumentException("Stream not found: $descriptor")
    }

    fun asProtocolObject(): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog().withStreams(streams.map { it.asProtocolObject() })

    fun size(): Int = streams.size

    internal fun throwIfInvalidDedupConfig() {
        streams.forEach { stream ->
            if (stream.importType is Dedupe) {
                stream.importType.primaryKey.forEach { pk ->
                    if (pk.isNotEmpty()) {
                        val firstPkElement = pk.first()
                        if (!stream.schema.asColumns().containsKey(firstPkElement)) {
                            throw ConfigErrorException(
                                "For stream ${stream.mappedDescriptor.toPrettyString()}: A primary key column does not exist in the schema: $firstPkElement"
                            )
                        }
                    }
                }
                if (stream.importType.cursor.isNotEmpty()) {
                    val firstCursorElement = stream.importType.cursor.first()
                    if (!stream.schema.asColumns().containsKey(firstCursorElement)) {
                        throw ConfigErrorException(
                            "For stream ${stream.mappedDescriptor.toPrettyString()}: The cursor does not exist in the schema: $firstCursorElement"
                        )
                    }
                }
            }
        }
    }
}

@Factory
class DefaultDestinationCatalogFactory {
    @Requires(property = Operation.PROPERTY, notEquals = "check")
    @Singleton
    fun syncCatalog(
        catalog: ConfiguredAirbyteCatalog,
        streamFactory: DestinationStreamFactory,
        tableNameResolver: TableNameResolver,
    ): DestinationCatalog {
        val descriptors =
            catalog.streams
                .map { DestinationStream.Descriptor(it.stream.namespace, it.stream.name) }
                .toSet()
        val names = tableNameResolver.getTableNameMapping(descriptors)

        return DestinationCatalog(
            streams =
                catalog.streams.map {
                    val key = DestinationStream.Descriptor(it.stream.namespace, it.stream.name)
                    streamFactory.make(it, names[key]!!)
                }
        )
    }

    /**
     * Warning: Most destinations do not use this.
     *
     * Catalog stub for running SYNC from within a CHECK operation.
     *
     * Used exclusively by the DefaultDestinationChecker.
     */
    @Requires(property = Operation.PROPERTY, value = "check")
    @Singleton
    fun checkCatalog(
        @Named("checkNamespace") checkNamespace: String?,
        namespaceMapper: NamespaceMapper
    ): DestinationCatalog {
        // generate a string like "20240523"
        val date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"))
        // generate 5 random characters
        val random = RandomStringUtils.insecure().nextAlphabetic(5).lowercase()
        val namespace = checkNamespace ?: "${CHECK_STREAM_NAMESPACE}_$date$random"
        return DestinationCatalog(
            listOf(
                DestinationStream(
                    unmappedNamespace = namespace,
                    unmappedName = "test$date$random",
                    importType = Append,
                    schema =
                        ObjectType(linkedMapOf("test" to FieldType(IntegerType, nullable = true))),
                    generationId = 1,
                    minimumGenerationId = 0,
                    syncId = 1,
                    namespaceMapper = namespaceMapper,
                    tableSchema =
                        StreamTableSchema(
                            columnSchema =
                                ColumnSchema(
                                    inputSchema = mapOf(),
                                    inputToFinalColumnNames = mapOf(),
                                    finalSchema = mapOf()
                                ),
                            importType = Append,
                            tableNames =
                                TableNames(
                                    finalTableName = TableName("namespace", "test"),
                                ),
                        ),
                )
            )
        )
    }
}
