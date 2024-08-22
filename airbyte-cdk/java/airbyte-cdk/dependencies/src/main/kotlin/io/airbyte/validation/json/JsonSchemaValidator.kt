/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.validation.json

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.networknt.schema.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.IOException
import java.net.URI
import java.net.URISyntaxException
import me.andrz.jackson.JsonContext
import me.andrz.jackson.JsonReferenceException
import me.andrz.jackson.JsonReferenceProcessor

private val LOGGER = KotlinLogging.logger {}

class JsonSchemaValidator @VisibleForTesting constructor(private val baseUri: URI?) {
    private val jsonSchemaFactory: JsonSchemaFactory =
        JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7)
    private val schemaToValidators: MutableMap<String, JsonSchema> = HashMap()

    constructor() : this(DEFAULT_BASE_URI)

    /**
     * Create and cache a schema validator for a particular schema. This validator is used when
     * [.testInitializedSchema] and [.ensureInitializedSchema] is called.
     */
    fun initializeSchemaValidator(schemaName: String, schemaJson: JsonNode) {
        schemaToValidators[schemaName] = getSchemaValidator(schemaJson)
    }

    /** Returns true if the object adheres to the given schema and false otherwise. */
    fun testInitializedSchema(schemaName: String, objectJson: JsonNode?): Boolean {
        val schema = schemaToValidators[schemaName]
        Preconditions.checkNotNull(
            schema,
            "$schemaName needs to be initialised before calling this method"
        )

        val validate = schema!!.validate(objectJson)
        return validate.isEmpty()
    }

    /** Throws an exception if the object does not adhere to the given schema. */
    @Throws(JsonValidationException::class)
    fun ensureInitializedSchema(schemaName: String, objectNode: JsonNode?) {
        val schema = schemaToValidators[schemaName]
        Preconditions.checkNotNull(
            schema,
            "$schemaName needs to be initialised before calling this method"
        )

        val validationMessages = schema!!.validate(objectNode)
        if (validationMessages.isEmpty()) {
            return
        }
        throw JsonValidationException(
            String.format(
                "json schema validation failed when comparing the data to the json schema. \nErrors: %s \nSchema: \n%s",
                validationMessages.joinToString(", "),
                schemaName
            )
        )
    }

    /**
     * WARNING
     *
     * The following methods perform JSON validation **by re-creating a validator each time**. This
     * is both CPU and GC expensive, and should be used carefully.
     */
    // todo(davin): Rewrite this section to cache schemas.
    fun test(schemaJson: JsonNode, objectJson: JsonNode): Boolean {
        val validationMessages = validateInternal(schemaJson, objectJson)

        if (validationMessages.isNotEmpty()) {
            LOGGER.info {
                "JSON schema validation failed. \nerrors: ${validationMessages.joinToString(", ")}"
            }
        }

        return validationMessages.isEmpty()
    }

    fun validate(schemaJson: JsonNode, objectJson: JsonNode): Set<String> {
        return validateInternal(schemaJson, objectJson)
            .map { obj: ValidationMessage -> obj.message }
            .toSet()
    }

    fun getValidationMessageArgs(schemaJson: JsonNode, objectJson: JsonNode): List<Array<String>> {
        return validateInternal(schemaJson, objectJson).map { obj: ValidationMessage ->
            obj.arguments
        }
    }

    fun getValidationMessagePaths(schemaJson: JsonNode, objectJson: JsonNode): List<String> {
        return validateInternal(schemaJson, objectJson).map { obj: ValidationMessage -> obj.path }
    }

    @Throws(JsonValidationException::class)
    fun ensure(schemaJson: JsonNode, objectJson: JsonNode) {
        val validationMessages = validateInternal(schemaJson, objectJson)
        if (validationMessages.isEmpty()) {
            return
        }

        throw JsonValidationException(
            String.format(
                "json schema validation failed when comparing the data to the json schema. \nErrors: %s \nSchema: \n%s",
                validationMessages.joinToString(", "),
                schemaJson.toPrettyString()
            )
        )
    }

    fun ensureAsRuntime(schemaJson: JsonNode, objectJson: JsonNode) {
        try {
            ensure(schemaJson, objectJson)
        } catch (e: JsonValidationException) {
            throw RuntimeException(e)
        }
    }

    // keep this internal as it returns a type specific to the wrapped library.
    private fun validateInternal(
        schemaJson: JsonNode,
        objectJson: JsonNode
    ): Set<ValidationMessage> {
        Preconditions.checkNotNull(schemaJson)
        Preconditions.checkNotNull(objectJson)

        val schema = getSchemaValidator(schemaJson)
        return schema.validate(objectJson)
    }

    /** Return a schema validator for a json schema, defaulting to the V7 Json schema. */
    private fun getSchemaValidator(schemaJson: JsonNode): JsonSchema {
        // Default to draft-07, but have handling for the other metaschemas that networknt supports
        val metaschema: JsonMetaSchema
        val metaschemaNode = schemaJson["\$schema"]
        if (metaschemaNode?.asText() == null || metaschemaNode.asText().isEmpty()) {
            metaschema = JsonMetaSchema.getV7()
        } else {
            val metaschemaString = metaschemaNode.asText()
            // We're not using "http://....".equals(), because we want to avoid weirdness with
            // https, etc.
            metaschema =
                if (metaschemaString.contains("json-schema.org/draft-04")) {
                    JsonMetaSchema.getV4()
                } else if (metaschemaString.contains("json-schema.org/draft-06")) {
                    JsonMetaSchema.getV6()
                } else if (metaschemaString.contains("json-schema.org/draft/2019-09")) {
                    JsonMetaSchema.getV201909()
                } else if (metaschemaString.contains("json-schema.org/draft/2020-12")) {
                    JsonMetaSchema.getV202012()
                } else {
                    JsonMetaSchema.getV7()
                }
        }

        val context =
            ValidationContext(
                jsonSchemaFactory.uriFactory,
                null,
                metaschema,
                jsonSchemaFactory,
                null
            )
        val schema = JsonSchema(context, baseUri, schemaJson)
        return schema
    }

    companion object {

        // This URI just needs to point at any path in the same directory as
        // /app/WellKnownTypes.json
        // It's required for the JsonSchema#validate method to resolve $ref correctly.
        private var DEFAULT_BASE_URI: URI? = null

        init {
            try {
                DEFAULT_BASE_URI = URI("file:///app/nonexistent_file.json")
            } catch (e: URISyntaxException) {
                throw RuntimeException(e)
            }
        }

        /**
         * Get JsonNode for an object defined as the main object in a JsonSchema file. Able to
         * create the JsonNode even if the the JsonSchema refers to objects in other files.
         *
         * @param schemaFile
         * - the schema file
         * @return schema object processed from across all dependency files.
         */
        @JvmStatic
        fun getSchema(schemaFile: File?): JsonNode {
            try {
                return processor.process(schemaFile)
            } catch (e: IOException) {
                throw RuntimeException(e)
            } catch (e: JsonReferenceException) {
                throw RuntimeException(e)
            }
        }

        /**
         * Get JsonNode for an object defined in the "definitions" section of a JsonSchema file.
         * Able to create the JsonNode even if the the JsonSchema refers to objects in other files.
         *
         * @param schemaFile
         * - the schema file
         * @param definitionStructName
         * - get the schema from a struct defined in the "definitions" section of a JsonSchema file
         * (instead of the main object in that file).
         * @return schema object processed from across all dependency files.
         */
        fun getSchema(schemaFile: File?, definitionStructName: String?): JsonNode {
            try {
                val jsonContext = JsonContext(schemaFile)
                return processor.process(
                    jsonContext,
                    jsonContext.document["definitions"][definitionStructName]
                )
            } catch (e: IOException) {
                throw RuntimeException(e)
            } catch (e: JsonReferenceException) {
                throw RuntimeException(e)
            }
        }

        private val processor: JsonReferenceProcessor
            get() {
                // JsonReferenceProcessor follows $ref in json objects. Jackson does not natively
                // support
                // this.
                val jsonReferenceProcessor = JsonReferenceProcessor()
                jsonReferenceProcessor.maxDepth = -1 // no max.

                return jsonReferenceProcessor
            }
    }
}
