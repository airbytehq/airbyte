/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.kjetland.jackson.jsonSchema.JsonSchemaConfig
import com.kjetland.jackson.jsonSchema.JsonSchemaDraft
import com.kjetland.jackson.jsonSchema.JsonSchemaGenerator
import com.networknt.schema.JsonSchema
import com.networknt.schema.JsonSchemaFactory
import com.networknt.schema.SchemaValidatorsConfig
import com.networknt.schema.SpecVersion
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.jackson.MoreMappers

/**
 * A grab-bag of JSON utilities because the `Jsons` object doesn't yet support mapping to Kotlin
 * data classes. Also includes utilities for JSON schemas.
 */
object JsonUtils {

    fun <T> jsonNode(klazz: Class<T>, any: T): JsonNode =
        try {
            mapper.valueToTree(any)
        } catch (e: Exception) {
            throw ConfigErrorException("failed to parse $klazz instance as JsonNode")
        }

    fun <T> parseOne(klazz: Class<T>, json: String): T {
        val tree: JsonNode =
            try {
                mapper.readTree(json)
            } catch (e: Exception) {
                throw ConfigErrorException("malformed json value while parsing for $klazz", e)
            }
        return parseList(klazz, tree).firstOrNull()
            ?: throw ConfigErrorException("missing json value while parsing for $klazz")
    }

    fun <T> parseList(elementClass: Class<T>, json: String?): List<T> {
        val tree: JsonNode =
            try {
                mapper.readTree(json ?: "[]")
            } catch (e: Exception) {
                throw ConfigErrorException(
                    "malformed json value while parsing for $elementClass",
                    e
                )
            }
        return parseList(elementClass, tree)
    }

    fun <T> parseList(elementClass: Class<T>, tree: JsonNode): List<T> {
        val jsonList: List<JsonNode> = if (tree.isArray) tree.toList() else listOf(tree)
        val schemaNode: JsonNode = generator.generateJsonSchema(elementClass)
        val jsonSchema: JsonSchema = jsonSchemaFactory.getSchema(schemaNode, jsonSchemaConfig)
        for (element in jsonList) {
            val validationFailures = jsonSchema.validate(element)
            if (validationFailures.isNotEmpty()) {
                throw ConfigErrorException(
                    "$elementClass json schema violation: ${validationFailures.first()}"
                )
            }
        }
        return jsonList.map { parseUnvalidated(it, elementClass) }
    }

    fun <T> parseUnvalidated(jsonNode: JsonNode, klazz: Class<T>): T =
        try {
            mapper.treeToValue(jsonNode, klazz)
        } catch (e: Exception) {
            throw ConfigErrorException("failed to map valid json to $klazz ", e)
        }

    val generatorConfig: JsonSchemaConfig =
        JsonSchemaConfig.vanillaJsonSchemaDraft4()
            .withJsonSchemaDraft(JsonSchemaDraft.DRAFT_07)
            .withFailOnUnknownProperties(false)

    val generator = JsonSchemaGenerator(MoreMappers.initMapper(), generatorConfig)

    val mapper: ObjectMapper =
        MoreMappers.initMapper().apply {
            setSerializationInclusion(JsonInclude.Include.NON_NULL)
            registerModule(KotlinModule.Builder().build())
        }

    val jsonSchemaConfig = SchemaValidatorsConfig()

    val jsonSchemaFactory: JsonSchemaFactory =
        JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7)
}
