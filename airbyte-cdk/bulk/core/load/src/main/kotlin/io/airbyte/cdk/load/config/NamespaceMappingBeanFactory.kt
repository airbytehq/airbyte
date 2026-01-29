/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.util.deserializeToClass
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.File

@Factory
class NamespaceMappingBeanFactory {
    private val log = KotlinLogging.logger {}

    @Singleton
    @Named("dataChannelMedium")
    fun dataChannelMedium(
        @Value("\${airbyte.destination.core.data-channel.medium}")
        dataChannelMedium: DataChannelMedium
    ): DataChannelMedium {
        log.info { "Using data channel medium $dataChannelMedium" }
        return dataChannelMedium
    }

    @Singleton
    fun namespaceMapper(
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium,
        @Value("\${airbyte.destination.core.mappers.namespace-mapping-config-path}")
        namespaceMappingConfigPath: String
    ): NamespaceMapper {
        when (dataChannelMedium) {
            DataChannelMedium.STDIO -> {
                log.info {
                    "Going to use the given source value: ${NamespaceDefinitionType.SOURCE} for namespace"
                }
                return NamespaceMapper(NamespaceDefinitionType.SOURCE)
            }
            DataChannelMedium.SOCKET -> {
                log.info { "In a SOCKET scenario. Using alternate version of the NamespaceMapper" }
                val config =
                    File(namespaceMappingConfigPath)
                        .readText(Charsets.UTF_8)
                        .deserializeToClass(NamespaceMappingConfig::class.java)
                return NamespaceMapper(
                    namespaceDefinitionType = config.namespaceDefinitionType,
                    namespaceFormat = config.namespaceFormat,
                    streamPrefix = config.streamPrefix
                )
            }
        }
    }
}
