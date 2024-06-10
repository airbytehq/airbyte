/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss.helpers

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.util.ClassUtil
import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import io.airbyte.commons.json.Jsons.clone
import io.airbyte.commons.json.Jsons.`object`
import io.airbyte.commons.yaml.Yamls.deserialize
import io.airbyte.configoss.StandardDestinationDefinition
import io.airbyte.configoss.StandardSourceDefinition
import java.util.*

/**
 * This is a convenience class for the conversion of a list of source/destination definitions from
 * human-friendly yaml to processing friendly formats i.e. Java models or JSON. As this class
 * performs validation, it is recommended to use this class to deal with plain lists. An example of
 * such lists are Airbyte's master definition lists, which can be seen in the resources folder of
 * the airbyte-config-oss/seed module.
 *
 * In addition to usual deserialization validations, we check: 1) The given list contains no
 * duplicate names. 2) The given list contains no duplicate ids.
 *
 * Methods in these class throw Runtime exceptions upon validation failure.
 */
object YamlListToStandardDefinitions {
    private val CLASS_NAME_TO_ID_NAME: Map<String, String> =
        java.util.Map.ofEntries(
            AbstractMap.SimpleImmutableEntry(
                StandardDestinationDefinition::class.java.canonicalName,
                "destinationDefinitionId"
            ),
            AbstractMap.SimpleImmutableEntry(
                StandardSourceDefinition::class.java.canonicalName,
                "sourceDefinitionId"
            )
        )

    fun toStandardSourceDefinitions(yamlStr: String?): List<StandardSourceDefinition?> {
        return verifyAndConvertToModelList(StandardSourceDefinition::class.java, yamlStr)
    }

    fun toStandardDestinationDefinitions(yamlStr: String?): List<StandardDestinationDefinition?> {
        return verifyAndConvertToModelList(StandardDestinationDefinition::class.java, yamlStr)
    }

    fun verifyAndConvertToJsonNode(idName: String?, yamlStr: String?): JsonNode {
        val jsonNode = deserialize(yamlStr)
        checkYamlIsPresentWithNoDuplicates(jsonNode, idName)
        return jsonNode
    }

    @VisibleForTesting
    fun <T> verifyAndConvertToModelList(klass: Class<T>, yamlStr: String?): List<T?> {
        val jsonNode = deserialize(yamlStr)
        val idName = CLASS_NAME_TO_ID_NAME[klass.canonicalName]
        checkYamlIsPresentWithNoDuplicates(jsonNode, idName)
        return toStandardXDefinitions(jsonNode.elements(), klass)
    }

    private fun checkYamlIsPresentWithNoDuplicates(deserialize: JsonNode, idName: String?) {
        val presentDestList = deserialize.elements() != ClassUtil.emptyIterator<Any>()
        Preconditions.checkState(presentDestList, "Definition list is empty")
        checkNoDuplicateNames(deserialize.elements())
        checkNoDuplicateIds(deserialize.elements(), idName)
    }

    private fun checkNoDuplicateNames(iter: Iterator<JsonNode>) {
        val names = HashSet<String>()
        while (iter.hasNext()) {
            val element = clone(iter.next())
            val name = element["name"].asText()
            require(!names.contains(name)) { "Multiple records have the name: $name" }
            names.add(name)
        }
    }

    private fun checkNoDuplicateIds(fileIterator: Iterator<JsonNode>, idName: String?) {
        val ids = HashSet<String>()
        while (fileIterator.hasNext()) {
            val element = clone(fileIterator.next())
            val id = element[idName].asText()
            require(!ids.contains(id)) { "Multiple records have the id: $id" }
            ids.add(id)
        }
    }

    private fun <T> toStandardXDefinitions(iter: Iterator<JsonNode>, c: Class<T>): List<T?> {
        val iterable = Iterable { iter }
        val defList = ArrayList<T?>()
        for (n in iterable) {
            val def = `object`(n, c)
            defList.add(def)
        }
        return defList
    }
}
