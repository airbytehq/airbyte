/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.json

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.io.IOs
import io.airbyte.commons.resources.MoreResources
import io.airbyte.commons.util.MoreIterators
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import java.util.function.BiConsumer
import java.util.function.BiFunction
import java.util.function.Predicate

private val log = KotlinLogging.logger {}

// todo (cgardens) - we need the ability to identify jsonschemas that Airbyte considers invalid for
// a connector (e.g. "not" keyword).
object JsonSchemas {
    private const val JSON_SCHEMA_ENUM_KEY = "enum"
    private const val JSON_SCHEMA_TYPE_KEY = "type"
    const val JSON_SCHEMA_PROPERTIES_KEY = "properties"
    private const val JSON_SCHEMA_ITEMS_KEY = "items"

    // all JSONSchema types.
    private const val ARRAY_TYPE = "array"
    private const val OBJECT_TYPE = "object"
    private const val STRING_TYPE = "string"
    private const val ONE_OF_TYPE = "oneOf"
    private const val ALL_OF_TYPE = "allOf"
    private const val ANY_OF_TYPE = "anyOf"

    private val COMPOSITE_KEYWORDS: Set<String> =
        java.util.Set.of(ONE_OF_TYPE, ALL_OF_TYPE, ANY_OF_TYPE)

    /**
     * JsonSchema supports to ways of declaring type. `type: "string"` and `type: ["null",
     * "string"]`. This method will mutate a JsonNode with a type field so that the output type is
     * the array version.
     *
     * @param jsonNode
     * - a json object with children that contain types.
     */
    fun mutateTypeToArrayStandard(jsonNode: JsonNode) {
        if (jsonNode[JSON_SCHEMA_TYPE_KEY] != null && !jsonNode[JSON_SCHEMA_TYPE_KEY].isArray) {
            val type = jsonNode[JSON_SCHEMA_TYPE_KEY]
            (jsonNode as ObjectNode).putArray(JSON_SCHEMA_TYPE_KEY).add(type)
        }
    }

    /*
     * JsonReferenceProcessor relies on all the json in consumes being in a file system (not in a jar).
     * This method copies all the json configs out of the jar into a temporary directory so that
     * JsonReferenceProcessor can find them.
     */
    @JvmStatic
    fun <T> prepareSchemas(resourceDir: String, klass: Class<T>): Path {
        try {
            val filenames: List<String>
            MoreResources.listResources(klass, resourceDir).use { resources ->
                filenames =
                    resources
                        .map { p: Path -> p.fileName.toString() }
                        .filter { p: String -> p.endsWith(".yaml") }
                        .toList()
            }
            val configRoot = Files.createTempDirectory("schemas")
            for (filename in filenames) {
                IOs.writeFile(
                    configRoot,
                    filename,
                    MoreResources.readResource(String.format("%s/%s", resourceDir, filename))
                )
            }

            return configRoot
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    /**
     * Traverse a JsonSchema object. The provided consumer will be called at each node with the node
     * and the path to the node.
     *
     * @param jsonSchema
     * - JsonSchema object to traverse
     * @param consumer
     * - accepts the current node and the path to that node.
     */
    fun traverseJsonSchema(
        jsonSchema: JsonNode,
        consumer: BiConsumer<JsonNode, List<FieldNameOrList>>
    ) {
        traverseJsonSchemaInternal(jsonSchema, ArrayList(), consumer)
    }

    /**
     * Traverse a JsonSchema object. At each node, map a value.
     *
     * @param jsonSchema
     * - JsonSchema object to traverse
     * @param mapper
     * - accepts the current node and the path to that node. whatever is returned will be collected
     * and returned by the final collection.
     * @param <T> - type of objects being collected
     * @return
     * - collection of all items that were collected during the traversal. Returns a { @link
     * Collection } because there is no order or uniqueness guarantee so neither List nor Set make
     * sense. </T>
     */
    fun <T> traverseJsonSchemaWithCollector(
        jsonSchema: JsonNode,
        mapper: BiFunction<JsonNode?, List<FieldNameOrList>?, T>
    ): List<T> {
        // for the sake of code reuse, use the filtered collector method but makes sure the filter
        // always
        // returns true.
        return traverseJsonSchemaWithFilteredCollector(jsonSchema) {
            node: JsonNode?,
            path: List<FieldNameOrList> ->
            Optional.ofNullable(mapper.apply(node, path))
        }
    }

    /**
     * Traverse a JsonSchema object. At each node, optionally map a value.
     *
     * @param jsonSchema
     * - JsonSchema object to traverse
     * @param mapper
     * - accepts the current node and the path to that node. if it returns an empty optional,
     * nothing will be collected, otherwise, whatever is returned will be collected and returned by
     * the final collection.
     * @param <T> - type of objects being collected
     * @return
     * - collection of all items that were collected during the traversal. Returns values in
     * preoorder traversal order. </T>
     */
    fun <T> traverseJsonSchemaWithFilteredCollector(
        jsonSchema: JsonNode,
        mapper: BiFunction<JsonNode?, List<FieldNameOrList>, Optional<T>>
    ): List<T> {
        val collector: MutableList<T> = ArrayList()
        traverseJsonSchema(jsonSchema) { node: JsonNode?, path: List<FieldNameOrList> ->
            mapper.apply(node, path).ifPresent { e: T -> collector.add(e) }
        }
        return collector // make list unmodifiable
    }

    /**
     * Traverses a JsonSchema object. It returns the path to each node that meet the provided
     * condition. The paths are return in JsonPath format. The traversal is depth-first search
     * preoorder and values are returned in that order.
     *
     * @param obj
     * - JsonSchema object to traverse
     * @param predicate
     * - predicate to determine if the path for a node should be collected.
     * @return
     * - collection of all paths that were collected during the traversal.
     */
    fun collectPathsThatMeetCondition(
        obj: JsonNode,
        predicate: Predicate<JsonNode?>
    ): List<List<FieldNameOrList>> {
        return traverseJsonSchemaWithFilteredCollector(obj) {
            node: JsonNode?,
            path: List<FieldNameOrList> ->
            if (predicate.test(node)) {
                return@traverseJsonSchemaWithFilteredCollector Optional.of<List<FieldNameOrList>>(
                    path
                )
            } else {
                return@traverseJsonSchemaWithFilteredCollector Optional.empty<
                    List<FieldNameOrList>>()
            }
        }
    }

    /**
     * Recursive, depth-first implementation of { @link JsonSchemas#traverseJsonSchema(final
     * JsonNode jsonNode, final BiConsumer<JsonNode></JsonNode>, List<String>> consumer) }. Takes
     * path as argument so that the path can be passed to the consumer.
     *
     * @param jsonSchemaNode
     * - jsonschema object to traverse.
     * @param consumer
     * - consumer to be called at each node. it accepts the current node and the path to the node
     * from the root of the object passed at the root level invocation </String>
     */
    private fun traverseJsonSchemaInternal(
        jsonSchemaNode: JsonNode,
        path: List<FieldNameOrList>,
        consumer: BiConsumer<JsonNode, List<FieldNameOrList>>
    ) {
        require(jsonSchemaNode.isObject) {
            String.format(
                "json schema nodes should always be object nodes. path: %s actual: %s",
                path,
                jsonSchemaNode
            )
        }
        consumer.accept(jsonSchemaNode, path)
        // if type is missing assume object. not official JsonSchema, but it seems to be a common
        // compromise.
        val nodeTypes = getTypeOrObject(jsonSchemaNode)

        for (nodeType in nodeTypes) {
            when (nodeType) {
                ARRAY_TYPE -> {
                    val newPath: MutableList<FieldNameOrList> =
                        ArrayList(java.util.List.copyOf(path))
                    newPath.add(FieldNameOrList.list())
                    if (jsonSchemaNode.has(JSON_SCHEMA_ITEMS_KEY)) {
                        // hit every node.
                        traverseJsonSchemaInternal(
                            jsonSchemaNode[JSON_SCHEMA_ITEMS_KEY],
                            newPath,
                            consumer
                        )
                    } else {
                        log.warn {
                            "The array is missing an items field. The traversal is silently stopped. Current schema: $jsonSchemaNode"
                        }
                    }
                }
                OBJECT_TYPE -> {
                    val comboKeyWordOptional = getKeywordIfComposite(jsonSchemaNode)
                    if (jsonSchemaNode.has(JSON_SCHEMA_PROPERTIES_KEY)) {
                        val it = jsonSchemaNode[JSON_SCHEMA_PROPERTIES_KEY].fields()
                        while (it.hasNext()) {
                            val child = it.next()
                            val newPath: MutableList<FieldNameOrList> =
                                ArrayList(java.util.List.copyOf(path))
                            newPath.add(FieldNameOrList.fieldName(child.key))
                            traverseJsonSchemaInternal(child.value, newPath, consumer)
                        }
                    } else if (comboKeyWordOptional.isPresent) {
                        for (arrayItem in jsonSchemaNode[comboKeyWordOptional.get()]) {
                            traverseJsonSchemaInternal(arrayItem, path, consumer)
                        }
                    } else {
                        log.warn {
                            "The object is a properties key or a combo keyword. The traversal is silently stopped. Current schema: $jsonSchemaNode"
                        }
                    }
                }
            }
        }
    }

    /**
     * If the object uses JSONSchema composite functionality (e.g. oneOf, anyOf, allOf), detect it
     * and return which one it is using.
     *
     * @param node
     * - object to detect use of composite functionality.
     * @return the composite functionality being used, if not using composite functionality, empty.
     */
    private fun getKeywordIfComposite(node: JsonNode): Optional<String> {
        for (keyWord in COMPOSITE_KEYWORDS) {
            if (node.has(keyWord)) {
                return Optional.ofNullable(keyWord)
            }
        }
        return Optional.empty()
    }

    /**
     * Same logic as [.getType] except when no type is found, it defaults to type: Object.
     *
     * @param jsonSchema
     * - JSONSchema object
     * @return type of the node.
     */
    fun getTypeOrObject(jsonSchema: JsonNode): List<String> {
        val types = getType(jsonSchema)
        return if (types.isEmpty()) {
            java.util.List.of(OBJECT_TYPE)
        } else {
            types
        }
    }

    /**
     * Get the type of JSONSchema node. Uses JSONSchema types. Only returns the type of the
     * "top-level" node. e.g. if more nodes are nested underneath because it is an object or an
     * array, only the top level type is returned.
     *
     * @param jsonSchema
     * - JSONSchema object
     * @return type of the node.
     */
    fun getType(jsonSchema: JsonNode): List<String> {
        if (jsonSchema.has(JSON_SCHEMA_TYPE_KEY)) {
            return if (jsonSchema[JSON_SCHEMA_TYPE_KEY].isArray) {
                MoreIterators.toList(jsonSchema[JSON_SCHEMA_TYPE_KEY].iterator()).map {
                    obj: JsonNode ->
                    obj.asText()
                }
            } else {
                java.util.List.of(jsonSchema[JSON_SCHEMA_TYPE_KEY].asText())
            }
        }
        if (jsonSchema.has(JSON_SCHEMA_ENUM_KEY)) {
            return java.util.List.of(STRING_TYPE)
        }
        return emptyList()
    }

    /**
     * Provides a basic scheme for describing the path into a JSON object. Each element in the path
     * is either a field name or a list.
     *
     * This class is helpful in the case where fields can be any UTF-8 string, so the only simple
     * way to keep track of the different parts of a path without going crazy with escape characters
     * is to keep it in a list with list set aside as a special case.
     *
     * We prefer using this scheme instead of JSONPath in the tree traversal because, it is easier
     * to decompose a path in this scheme than it is in JSONPath. Some callers of the traversal
     * logic want to isolate parts of the path easily without the need for complex regex (that would
     * be required if we used JSONPath).
     */
    class FieldNameOrList private constructor(val fieldName: String?) {
        val isList: Boolean = fieldName == null

        override fun equals(other: Any?): Boolean {
            if (this === other) {
                return true
            }
            if (other !is FieldNameOrList) {
                return false
            }
            val that = other
            return isList == that.isList && fieldName == that.fieldName
        }

        override fun hashCode(): Int {
            return Objects.hash(fieldName, isList)
        }

        override fun toString(): String {
            return "FieldNameOrList{" +
                "fieldName='" +
                fieldName +
                '\'' +
                ", isList=" +
                isList +
                '}'
        }

        companion object {
            fun fieldName(fieldName: String?): FieldNameOrList {
                return FieldNameOrList(fieldName)
            }

            fun list(): FieldNameOrList {
                return FieldNameOrList(null)
            }
        }
    }
}
