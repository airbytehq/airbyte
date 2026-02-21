/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.module.kotlin.contains
import com.github.victools.jsonschema.generator.Option
import com.github.victools.jsonschema.generator.OptionPreset
import com.github.victools.jsonschema.generator.SchemaGenerator
import com.github.victools.jsonschema.generator.SchemaGeneratorConfigBuilder
import com.github.victools.jsonschema.generator.SchemaVersion
import com.github.victools.jsonschema.module.jackson.JacksonModule
import com.github.victools.jsonschema.module.jackson.JacksonOption
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.spec.AirbyteSchemaModule
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
        val schemaNode: JsonNode = generator.generateSchema(elementClass)
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
        json: String,
        klazz: Class<T>,
    ): T {
        val tree: JsonNode =
            try {
                Jsons.readTree(json)
            } catch (e: Exception) {
                throw ConfigErrorException("malformed json value while parsing for $klazz", e)
            }
        return parseUnvalidated(tree, klazz)
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

    private val generatorConfig =
        SchemaGeneratorConfigBuilder(
                Jsons,
                SchemaVersion.DRAFT_7,
                OptionPreset.PLAIN_JSON,
            )
            .with(Option.DEFINITIONS_FOR_ALL_OBJECTS)
            .with(Option.FLATTENED_ENUMS)
            .with(
                JacksonModule(
                    JacksonOption.RESPECT_JSONPROPERTY_REQUIRED,
                    JacksonOption.FLATTENED_ENUMS_FROM_JSONVALUE,
                ),
            )
            .with(AirbyteSchemaModule())
            .without(Option.SCHEMA_VERSION_INDICATOR)
            .build()

    private val generator = SchemaGenerator(generatorConfig)

    /**
     * Generates a JSON schema suitable for use by the Airbyte Platform.
     *
     * This entails inlining any "$ref" fields and ensuring that an object with a "oneOf" field also
     * contains `"type": "object"`.
     */
    fun <T> generateAirbyteJsonSchema(klazz: Class<T>): JsonNode {
        val root: ObjectNode = generator.generateSchema(klazz) as ObjectNode
        if (!root.contains("\$defs") && !root.contains("definitions")) {
            return root
        }
        val defsKey = if (root.contains("\$defs")) "\$defs" else "definitions"
        val definitions: ObjectNode = root[defsKey] as ObjectNode

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
                    val ref: String =
                        node["\$ref"]
                            .textValue()
                            .removePrefix("#/\$defs/")
                            .removePrefix("#/definitions/")
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
        walk(definitions)
        root.remove(defsKey)
        walk(root)
        return root
    }
}
