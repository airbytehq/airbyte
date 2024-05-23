/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.commons.text.Names
import io.airbyte.commons.util.MoreIterators

open class StandardNameTransformer : NamingConventionTransformer {
    override fun getIdentifier(name: String): String {
        return convertStreamName(name)
    }

    /** Most destinations have the same naming requirement for namespace and stream names. */
    override fun getNamespace(namespace: String): String {
        return convertStreamName(namespace)
    }

    // @Deprecated see https://github.com/airbytehq/airbyte/issues/35333
    @Deprecated("as this is very SQL specific, prefer using getIdentifier instead")
    override fun getRawTableName(name: String): String {
        return convertStreamName("_airbyte_raw_$name")
    }

    @Deprecated("as this is very SQL specific, prefer using getIdentifier instead")
    override fun getTmpTableName(name: String): String {
        return convertStreamName(Strings.addRandomSuffix("_airbyte_tmp", "_", 3) + "_" + name)
    }

    override fun getTmpTableName(streamName: String, randomSuffix: String): String {
        return convertStreamName("_airbyte_tmp" + "_" + randomSuffix + "_" + streamName)
    }

    override fun convertStreamName(input: String): String {
        return Names.toAlphanumericAndUnderscore(input)
    }

    override fun applyDefaultCase(input: String): String {
        return input
    }

    companion object {
        private const val NON_JSON_PATH_CHARACTERS_PATTERN = "['\"`]"

        /**
         * Rebuild a JsonNode adding sanitized property names (a subset of special characters
         * replaced by underscores) while keeping original property names too. This is needed by
         * some destinations as their json extract functions have limitations on how such special
         * characters are parsed. These naming rules may be different to schema/table/column naming
         * conventions.
         */
        @JvmStatic
        fun formatJsonPath(root: JsonNode): JsonNode {
            if (root.isObject) {
                val properties: MutableMap<String, JsonNode> = HashMap()
                val keys = Jsons.keys(root)
                for (key in keys) {
                    val property = root[key]
                    // keep original key
                    properties[key] = formatJsonPath(property)
                }
                for (key in keys) {
                    val property = root[key]
                    val formattedKey = key.replace(NON_JSON_PATH_CHARACTERS_PATTERN.toRegex(), "_")
                    if (!properties.containsKey(formattedKey)) {
                        // duplicate property in a formatted key to be extracted in normalization
                        properties[formattedKey] = formatJsonPath(property)
                    }
                }
                return Jsons.jsonNode<Map<String, JsonNode>>(properties)
            } else if (root.isArray) {
                return Jsons.jsonNode(
                    MoreIterators.toList(root.elements())
                        .stream()
                        .map { r: JsonNode -> formatJsonPath(r) }
                        .toList()
                )
            } else {
                return root
            }
        }
    }
}
