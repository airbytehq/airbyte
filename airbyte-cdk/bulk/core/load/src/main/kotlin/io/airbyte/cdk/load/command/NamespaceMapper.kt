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

    private val template: Template? =
        if (
            namespaceDefinitionType == NamespaceDefinitionType.CUSTOM_FORMAT &&
                !namespaceFormat.isNullOrBlank()
        ) {
            val parts = namespaceFormat.split("\${SOURCE_NAMESPACE}", limit = 2)
            Template(parts[0], parts.getOrElse(1) { "" })
        } else null

    private data class Key(val ns: String?, val name: String) {
        private val hc: Int = 31 * (ns?.hashCode() ?: 0) + name.hashCode()
        override fun hashCode() = hc
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
                NamespaceDefinitionType.CUSTOM_FORMAT -> template?.build(sourceNamespace)
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

    private class Template(private val pre: String, private val post: String) {
        fun build(sourceNs: String?): String? {
            val ns = sourceNs ?: ""
            if (pre.isEmpty() && post.isEmpty()) return ns.ifBlank { null }
            val result =
                buildString(pre.length + ns.length + post.length) {
                    append(pre)
                    append(ns)
                    append(post)
                }
            return result.ifBlank { null }
        }
    }
}
