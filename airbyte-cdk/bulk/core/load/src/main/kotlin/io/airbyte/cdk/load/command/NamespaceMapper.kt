/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.config.NamespaceDefinitionType
import java.util.concurrent.ConcurrentHashMap

class NamespaceMapper(
    private val namespaceDefinitionType: NamespaceDefinitionType = NamespaceDefinitionType.SOURCE,
    private val namespaceFormat: String? = null,
    private val streamPrefix: String? = null,
) {

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is NamespaceMapper) return false

        return namespaceDefinitionType == other.namespaceDefinitionType &&
            namespaceFormat == other.namespaceFormat &&
            streamPrefix == other.streamPrefix
    }

    override fun hashCode(): Int {
        var result = namespaceDefinitionType.hashCode()
        result = 31 * result + (namespaceFormat?.hashCode() ?: 0)
        result = 31 * result + (streamPrefix?.hashCode() ?: 0)
        return result
    }

    private val hasPrefix = !streamPrefix.isNullOrBlank()
    private val prefix = streamPrefix ?: ""

    private data class Key(val ns: String?, val name: String) {
        private val hc: Int = 31 * (ns?.hashCode() ?: 0) + name.hashCode()
        override fun hashCode() = hc
        override fun equals(other: Any?): Boolean {
            if (this === other) return true
            if (javaClass != other?.javaClass) return false

            other as Key

            if (hc != other.hc) return false
            if (ns != other.ns) return false
            if (name != other.name) return false

            return true
        }
    }

    private val cache = ConcurrentHashMap<Key, DestinationStream.Descriptor>(128)

    fun map(namespace: String?, name: String): DestinationStream.Descriptor {
        val key = Key(namespace, name)

        cache[key]?.let {
            return it
        }

        val computed = doMap(namespace, name)
        return cache.computeIfAbsent(key) { computed }
    }

    fun unmap(d: DestinationStream.Descriptor): Pair<String?, String> = d.namespace to d.name

    private fun doMap(sourceNamespace: String?, streamName: String): DestinationStream.Descriptor {
        val mappedNs =
            when (namespaceDefinitionType) {
                NamespaceDefinitionType.SOURCE -> sourceNamespace
                NamespaceDefinitionType.DESTINATION -> null // default
                NamespaceDefinitionType.CUSTOM_FORMAT ->
                    formatNamespace(sourceNamespace, namespaceFormat)
            }

        val mappedName =
            if (hasPrefix)
                buildString(prefix.length + streamName.length) {
                    append(prefix)
                    append(streamName)
                }
            else streamName

        return DestinationStream.Descriptor(namespace = mappedNs, name = mappedName)
    }

    private fun formatNamespace(sourceNamespace: String?, namespaceFormat: String?): String? {
        if (namespaceFormat.isNullOrBlank()) return null

        val replaceWith = sourceNamespace?.takeIf { it.isNotBlank() } ?: ""
        val result = namespaceFormat.replace("\${SOURCE_NAMESPACE}", replaceWith)

        return result.ifBlank { null }
    }
}
