/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.config.CHECK_STREAM_NAMESPACE
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
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
        streams.associateBy { it.descriptor }

    init {
        if (streams.isEmpty()) {
            throw IllegalArgumentException(
                "Catalog must have at least one stream: check that files are in the correct location."
            )
        }
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
}

interface DestinationCatalogFactory {
    fun make(): DestinationCatalog
}

@Factory
class DefaultDestinationCatalogFactory {
    @Singleton
    fun getDestinationCatalog(
        catalog: ConfiguredAirbyteCatalog,
        streamFactory: DestinationStreamFactory,
        @Value("\${${Operation.PROPERTY}}") operation: String,
        @Named("checkNamespace") checkNamespace: String?,
        namespaceMapper: NamespaceMapper
    ): DestinationCatalog {
        if (operation == "check") {
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
            return DestinationCatalog(streams = catalog.streams.map { streamFactory.make(it) })
        }
    }
}
