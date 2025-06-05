/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.config.NamespaceDefinitionType

data class NamespaceMapper(
    private val namespaceDefinitionType: NamespaceDefinitionType =
        NamespaceDefinitionType.SOURCE, // ie, identity
    private val namespaceFormat: String? = null,
    private val streamPrefix: String? = null,
) {
    fun map(namespace: String?, name: String): DestinationStream.Descriptor {
        val newNamespace =
            when (namespaceDefinitionType) {
                NamespaceDefinitionType.SOURCE -> namespace
                NamespaceDefinitionType.DESTINATION -> null
                NamespaceDefinitionType.CUSTOM_FORMAT ->
                    formatNamespace(
                        sourceNamespace = namespace,
                        namespaceFormat = namespaceFormat,
                    )
            } // null implies namespace default
        val newName = transformStreamName(streamName = name, streamPrefix = streamPrefix)
        return DestinationStream.Descriptor(
            namespace = newNamespace,
            name = newName,
        )
    }

    // Copied from platform code.
    private fun formatNamespace(
        sourceNamespace: String?,
        namespaceFormat: String?,
    ): String? {
        var result: String? = ""
        namespaceFormat
            ?.takeIf { it.isNotBlank() }
            ?.let { format ->
                val replaceWith = sourceNamespace?.takeIf { it.isNotBlank() } ?: ""
                result = format.replace("\${SOURCE_NAMESPACE}", replaceWith)
            }

        return if (result.isNullOrBlank()) {
            null
        } else {
            result
        }
    }

    // Copied from platform code
    private fun transformStreamName(
        streamName: String,
        streamPrefix: String?,
    ): String =
        if (streamPrefix.isNullOrBlank()) {
            streamName
        } else {
            streamPrefix + streamName
        }

    fun unmap(descriptor: DestinationStream.Descriptor): Pair<String?, String> {
        return Pair(descriptor.namespace, descriptor.name)
    }
}
