/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.google.common.base.Preconditions
import com.jayway.jsonpath.Configuration
import com.jayway.jsonpath.JsonPath
import com.jayway.jsonpath.Option
import com.jayway.jsonpath.PathNotFoundException
import com.jayway.jsonpath.spi.json.JacksonJsonNodeJsonProvider
import com.jayway.jsonpath.spi.json.JsonProvider
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider
import com.jayway.jsonpath.spi.mapper.MappingProvider
import io.airbyte.commons.util.MoreIterators
import java.util.*
import java.util.function.BiFunction
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * JSONPath is specification for querying JSON objects. More information about the specification can
 * be found here: https://goessner.net/articles/JsonPath/. For those familiar with jq, JSONPath will
 * be most recognizable as "that DSL that jq uses".
 *
 * We use a java implementation of this specification (repo: https://github.com/json-path/JsonPath).
 * This class wraps that implementation to make it easier to leverage this tool internally.
 *
 * GOTCHA: Keep in mind with JSONPath, depending on the query, 0, 1, or N values may be returned.
 * The pattern for handling return values is very much like writing SQL queries. When using it, you
 * must consider what the number of return values for your query might be. e.g. for this object: {
 * "alpha": [1, 2, 3] }, this JSONPath "$.alpha[*]", would return: [1, 2, 3], but this one
 * "$.alpha[0]" would return: [1]. The Java interface we place over this query system defaults to
 * returning a list for query results. In addition, we provide helper functions that will just
 * return a single value (see: [JsonPaths.getSingleValue]). These should only be used if it is not
 * possible for a query to return more than one value.
 */
object JsonPaths {
    private val LOGGER: Logger = LoggerFactory.getLogger(JsonPaths::class.java)

    const val JSON_PATH_START_CHARACTER: String = "$"
    const val JSON_PATH_LIST_SPLAT: String = "[*]"
    const val JSON_PATH_FIELD_SEPARATOR: String = "."

    // set default configurations at start up to match our JSON setup.
    init {
        Configuration.setDefaults(
            object : Configuration.Defaults {
                // allows us to pass in Jackson JsonNode
                private val jsonProvider: JsonProvider = JacksonJsonNodeJsonProvider()
                private val mappingProvider: MappingProvider = JacksonMappingProvider()

                override fun jsonProvider(): JsonProvider {
                    return jsonProvider
                }

                override fun mappingProvider(): MappingProvider {
                    return mappingProvider
                }

                override fun options(): Set<Option> {
                    /*
                     * All JsonPath queries will return a list of values. This makes parsing the outputs much easier. In
                     * cases where it is not a list, helpers in this class can assert that. See
                     * https://github.com/json-path/JsonPath in the JsonPath documentation.
                     */
                    return EnumSet.of(Option.ALWAYS_RETURN_LIST)
                }
            }
        )
    }

    fun empty(): String {
        return JSON_PATH_START_CHARACTER
    }

    fun appendField(jsonPath: String, field: String?): String {
        return jsonPath + JSON_PATH_FIELD_SEPARATOR + field
    }

    fun appendAppendListSplat(jsonPath: String): String {
        return jsonPath + JSON_PATH_LIST_SPLAT
    }

    /**
     * Map path produced by [JsonSchemas] to the JSONPath format.
     *
     * @param jsonSchemaPath
     * - path as described in [JsonSchemas]
     * @return path as JSONPath
     */
    fun mapJsonSchemaPathToJsonPath(jsonSchemaPath: List<JsonSchemas.FieldNameOrList>): String {
        var jsonPath = empty()
        for (fieldNameOrList in jsonSchemaPath) {
            jsonPath =
                if (fieldNameOrList.isList) appendAppendListSplat(jsonPath)
                else appendField(jsonPath, fieldNameOrList.fieldName)
        }
        return jsonPath
    }

    /*
     * This version of the JsonPath Configuration object allows queries to return to the path of values
     * instead of the values that were found.
     */
    private val GET_PATHS_CONFIGURATION: Configuration =
        Configuration.defaultConfiguration().addOptions(Option.AS_PATH_LIST)

    /**
     * Attempt to validate if a string is a valid JSONPath string. This assertion does NOT handle
     * all cases, but at least a common on. We can add to it as we detect others.
     *
     * @param jsonPath
     * - path to validate
     */
    fun assertIsJsonPath(jsonPath: String) {
        Preconditions.checkArgument(jsonPath.startsWith("$"))
    }

    /**
     * Attempt to detect if a JSONPath query could return more than 1 value. This assertion does NOT
     * handle all cases, but at least a common on. We can add to it as we detect others.
     *
     * @param jsonPath
     * - path to validate
     */
    fun assertIsSingleReturnQuery(jsonPath: String?) {
        Preconditions.checkArgument(
            JsonPath.isPathDefinite(jsonPath),
            "Cannot accept paths with wildcards because they may return more than one item."
        )
    }

    /**
     * Given a JSONPath, returns all the values that match that path.
     *
     * e.g. for this object: { "alpha": [1, 2, 3] }, if the input JSONPath were "$.alpha[*]", this
     * function would return: [1, 2, 3].
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @return all values that match the input query
     */
    fun getValues(json: JsonNode?, jsonPath: String): List<JsonNode> {
        return getInternal(Configuration.defaultConfiguration(), json, jsonPath)
    }

    /**
     * Given a JSONPath, returns all the path of all values that match that path.
     *
     * e.g. for this object: { "alpha": [1, 2, 3] }, if the input JSONPath were "$.alpha[*]", this
     * function would return: ["$.alpha[0]", "$.alpha[1]", "$.alpha[2]"].
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @return all paths that are present that match the input query. returns a list (instead of a
     * set), because having a deterministic ordering is valuable for all downstream consumers (i.e.
     * in most cases if we returned a set, the downstream would then put it in a set and sort it so
     * that if they are doing replacements using the paths, the behavior is predictable e.g. if you
     * do replace $.alpha and $.alpha[*], the order you do those replacements in matters).
     * specifically that said, we do expect that there will be no duplicates in the returned list.
     */
    fun getPaths(json: JsonNode?, jsonPath: String): List<String> {
        return getInternal(GET_PATHS_CONFIGURATION, json, jsonPath).map { obj: JsonNode ->
            obj.asText()
        }
    }

    /**
     * Given a JSONPath, returns 1 or 0 values that match the path. Throws if more than 1 value is
     * found.
     *
     * THIS SHOULD ONLY BE USED IF THE JSONPATH CAN ONLY EVER RETURN 0 OR 1 VALUES. e.g. don't do
     * "$.alpha[*]"
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @return value if present, otherwise empty.
     */
    fun getSingleValue(json: JsonNode?, jsonPath: String): Optional<JsonNode> {
        assertIsSingleReturnQuery(jsonPath)

        val jsonNodes = getValues(json, jsonPath)

        Preconditions.checkState(
            jsonNodes.size <= 1,
            String.format(
                "Path returned more than one item. path: %s items: %s",
                jsonPath,
                jsonNodes
            )
        )
        return if (jsonNodes.isEmpty()) Optional.empty() else Optional.of(jsonNodes[0])
    }

    /**
     * Given a JSONPath, true if path is present in the object, otherwise false. Throws is more than
     * 1 path is found.
     *
     * THIS SHOULD ONLY BE USED IF THE JSONPATH CAN ONLY EVER RETURN 0 OR 1 VALUES. e.g. don't do
     * "$.alpha[*]"
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @return true if path is present in the object, otherwise false.
     */
    fun isPathPresent(json: JsonNode?, jsonPath: String): Boolean {
        assertIsSingleReturnQuery(jsonPath)

        val foundPaths = getPaths(json, jsonPath)

        Preconditions.checkState(
            foundPaths.size <= 1,
            String.format(
                "Path returned more than one item. path: %s items: %s",
                jsonPath,
                foundPaths
            )
        )
        return !foundPaths.isEmpty()
    }

    /**
     * Traverses into a json object and replaces all values that match the input path with the
     * provided string. Throws if no existing fields match the path.
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @param replacement
     * - a string value to replace the current value at the jsonPath
     * @throws PathNotFoundException throws if the path is not present in the object
     */
    fun replaceAtStringLoud(json: JsonNode, jsonPath: String, replacement: String): JsonNode {
        return replaceAtJsonNodeLoud(json, jsonPath, Jsons.jsonNode(replacement))
    }

    /**
     * Traverses into a json object and replaces all values that match the input path with the
     * provided string . Does nothing if no existing fields match the path.
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @param replacement
     * - a string value to replace the current value at the jsonPath
     */
    fun replaceAtString(json: JsonNode, jsonPath: String, replacement: String): JsonNode {
        return replaceAtJsonNode(json, jsonPath, Jsons.jsonNode(replacement))
    }

    /**
     * Traverses into a json object and replaces all values that match the input path with the
     * provided json object. Does nothing if no existing fields match the path.
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @param replacement
     * - a json node to replace the current value at the jsonPath
     */
    fun replaceAtJsonNodeLoud(json: JsonNode, jsonPath: String, replacement: JsonNode?): JsonNode {
        assertIsJsonPath(jsonPath)
        return JsonPath.parse(Jsons.clone(json)).set(jsonPath, replacement).json()
    }

    /**
     * Traverses into a json object and replaces all values that match the input path with the
     * provided json object. Does nothing if no existing fields match the path.
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @param replacement
     * - a json node to replace the current value at the jsonPath
     */
    fun replaceAtJsonNode(json: JsonNode, jsonPath: String, replacement: JsonNode?): JsonNode {
        try {
            return replaceAtJsonNodeLoud(json, jsonPath, replacement)
        } catch (e: PathNotFoundException) {
            LOGGER.debug("Path not found", e)
            return Jsons.clone(json) // defensive copy in failure case.
        }
    }

    /**
     * Traverses into a json object and replaces all values that match the input path with the
     * output of the provided function. Does nothing if no existing fields match the path.
     *
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @param replacementFunction
     * - a function that takes in a node that matches the path as well as the path to the node
     * itself. the return of this function will replace the current node.
     */
    fun replaceAt(
        json: JsonNode,
        jsonPath: String,
        replacementFunction: BiFunction<JsonNode, String, JsonNode>
    ): JsonNode {
        var clone = Jsons.clone(json)
        assertIsJsonPath(jsonPath)
        val foundPaths = getPaths(clone, jsonPath)
        for (foundPath in foundPaths) {
            val singleValue = getSingleValue(clone, foundPath)
            if (singleValue.isPresent) {
                val replacement = replacementFunction.apply(singleValue.get(), foundPath)
                clone = replaceAtJsonNode(clone, foundPath, replacement)
            }
        }
        return clone
    }

    /**
     *
     * @param conf
     * - JsonPath configuration. Primarily used to reuse code to allow fetching values or paths from
     * a json object
     * @param json
     * - json object
     * @param jsonPath
     * - path into the json object. must be in the format of JSONPath.
     * @return all values that match the input query (whether the values are paths or actual values
     * in the json object is determined by the conf)
     */
    private fun getInternal(
        conf: Configuration,
        json: JsonNode?,
        jsonPath: String
    ): List<JsonNode> {
        assertIsJsonPath(jsonPath)
        return try {
            MoreIterators.toList(
                JsonPath.using(conf).parse(json).read(jsonPath, ArrayNode::class.java).iterator()
            )
        } catch (e: PathNotFoundException) {
            emptyList()
        }
    }
}
