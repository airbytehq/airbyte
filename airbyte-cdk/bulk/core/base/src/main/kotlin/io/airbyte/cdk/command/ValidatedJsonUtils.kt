/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.module.kotlin.contains
import com.kjetland.jackson.jsonSchema.JsonSchemaConfig
import com.kjetland.jackson.jsonSchema.JsonSchemaDraft
import com.kjetland.jackson.jsonSchema.JsonSchemaGenerator
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import org.openapi4j.core.validation.ValidationException
import org.openapi4j.core.validation.ValidationResults
import org.openapi4j.schema.validator.ValidationData
import org.openapi4j.schema.validator.v3.SchemaValidator

object ValidatedJsonUtils {
    fun <T> parseOne(
        klazz: Class<T>,
        json: String,
    ): T {
        val tree: JsonNode =
            try {
                Jsons.readTree(json)
            } catch (e: Exception) {
                throw ConfigErrorException("malformed json value while parsing for $klazz", e)
            }
        return parseList(klazz, tree).firstOrNull()
            ?: throw ConfigErrorException("missing json value while parsing for $klazz")
    }

    fun <T> parseList(
        elementClass: Class<T>,
        json: String?,
    ): List<T> {
        val tree: JsonNode =
            try {
                Jsons.readTree(json ?: "[]")
            } catch (e: Exception) {
                throw ConfigErrorException(
                    "malformed json value while parsing for $elementClass",
                    e,
                )
            }
        return parseList(elementClass, tree)
    }

    fun <T> parseList(
        elementClass: Class<T>,
        tree: JsonNode,
    ): List<T> {
        val jsonList: List<JsonNode> = if (tree.isArray) tree.toList() else listOf(tree)
        val schemaNode: JsonNode = generator.generateJsonSchema(elementClass)
        val schemaValidator = SchemaValidator(null, schemaNode)
        for (element in jsonList) {
            val validationData = ValidationData<Void>()
            schemaValidator.validate(element, validationData)
            val validationResults: ValidationResults = validationData.results()
            if (!validationResults.isValid) {
                val prefix = "$elementClass schema violation"
                throw ConfigErrorException(
                    displayMessage = "$prefix: $validationResults",
                    exception = ValidationException(prefix, validationResults),
                )
            }
        }
        return jsonList.map { parseUnvalidated(it, elementClass) }
    }

    fun <T> parseUnvalidated(
        jsonNode: JsonNode,
        klazz: Class<T>,
    ): T =
        try {
            Jsons.treeToValue(jsonNode, klazz)
        } catch (e: Exception) {
            throw ConfigErrorException("failed to map valid json to $klazz ", e)
        }

    val generatorConfig: JsonSchemaConfig =
        JsonSchemaConfig.vanillaJsonSchemaDraft4()
            .withJsonSchemaDraft(JsonSchemaDraft.DRAFT_07)
            .withFailOnUnknownProperties(false)

    private val generator = JsonSchemaGenerator(Jsons, generatorConfig)

    /**
     * Generates a JSON schema suitable for use by the Airbyte Platform.
     *
     * This entails inlining any "$ref" fields and ensuring that an object with a "oneOf" field also
     * contains `"type": "object"`.
     */
    fun <T> generateAirbyteJsonSchema(klazz: Class<T>): JsonNode {
        // Generate the real JSON schema for the class object.
        val root: ObjectNode = generator.generateJsonSchema(klazz) as ObjectNode
        // Now perform any post-processing required by Airbyte.
        if (!root.contains("definitions")) {
            // Nothing needs to be done where there are no "$ref" fields anywhere.
            // This implies that there will be no "oneOf"s either.
            return root
        }
        val definitions: ObjectNode = root["definitions"] as ObjectNode

        fun walk(
            node: JsonNode,
            vararg visitedRefs: String,
        ) {
            when (node) {
                is ArrayNode ->
                    // Recurse over all array elements.
                    for (e in node.elements()) walk(e, *visitedRefs)
                is ObjectNode -> {
                    if (node.contains("oneOf")) {
                        // Insert superfluous `"type": "object"` entry into object containing
                        // "oneOf".
                        // This doesn't change the schema but it makes the platform happy.
                        node.set<JsonNode>("type", Jsons.textNode("object"))
                    }
                    if (!node.contains("\$ref")) {
                        // Nothing to inline here, just recurse over all object field values.
                        for (pair in node.fields()) {
                            walk(pair.value, *visitedRefs)
                        }
                        return
                    }
                    // Inline the type referenced by the "$ref" field.
                    val ref: String = node["\$ref"].textValue().removePrefix("#/definitions/")
                    if (ref in visitedRefs) {
                        throw ConfigErrorException("circular \$ref '$ref' found in JSON schema")
                    }
                    val definition: ObjectNode =
                        definitions[ref] as? ObjectNode
                            ?: throw ConfigErrorException(
                                "Undefined \$ref '$ref' found in JSON schema",
                            )
                    for (pair in definition.fields()) {
                        // Inline the definition in the current object.
                        // When a key is already present, keep the existing value.
                        if (!node.contains(pair.key)) {
                            node.set<JsonNode>(pair.key, pair.value)
                        }
                    }
                    node.remove("\$ref")
                    // Recurse over the object field values, including those which have just been
                    // inlined.
                    for (pair in node.fields()) {
                        walk(pair.value, ref, *visitedRefs)
                    }
                }
                else ->
                    // Nothing to do for non-array-non-object JSON nodes.
                    return
            }
        }
        // Flatten the definitions first, to check for circular references.
        walk(definitions)
        // Remove the definitions, as they will be inlined.
        root.remove("definitions")
        // Inline the definitions.
        walk(root)
        // Return the transformed object.
        return root
    }
}
