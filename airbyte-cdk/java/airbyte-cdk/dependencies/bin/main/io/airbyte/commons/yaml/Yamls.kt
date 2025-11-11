/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.yaml

import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.core.JsonToken
import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SequenceWriter
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator
import com.google.common.collect.AbstractIterator
import io.airbyte.commons.concurrency.VoidCallable
import io.airbyte.commons.jackson.MoreMappers.initYamlMapper
import io.airbyte.commons.lang.CloseableConsumer
import io.airbyte.commons.lang.Exceptions.toRuntime
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import java.io.IOException
import java.io.InputStream
import java.io.Writer

object Yamls {
    private val YAML_FACTORY = YAMLFactory()
    private val OBJECT_MAPPER = initYamlMapper(YAML_FACTORY)

    private val YAML_FACTORY_WITHOUT_QUOTES: YAMLFactory =
        YAMLFactory().enable(YAMLGenerator.Feature.MINIMIZE_QUOTES)
    private val OBJECT_MAPPER_WITHOUT_QUOTES = initYamlMapper(YAML_FACTORY_WITHOUT_QUOTES)

    /**
     * Serialize object to YAML string. String values WILL be wrapped in double quotes.
     *
     * @param object
     * - object to serialize
     * @return YAML string version of object
     */
    fun <T> serialize(`object`: T): String {
        try {
            return OBJECT_MAPPER.writeValueAsString(`object`)
        } catch (e: JsonProcessingException) {
            throw RuntimeException(e)
        }
    }

    /**
     * Serialize object to YAML string. String values will NOT be wrapped in double quotes.
     *
     * @param object
     * - object to serialize
     * @return YAML string version of object
     */
    fun serializeWithoutQuotes(`object`: Any?): String {
        try {
            return OBJECT_MAPPER_WITHOUT_QUOTES.writeValueAsString(`object`)
        } catch (e: JsonProcessingException) {
            throw RuntimeException(e)
        }
    }

    fun <T> deserialize(yamlString: String?, klass: Class<T>?): T {
        try {
            return OBJECT_MAPPER.readValue(yamlString, klass)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    fun <T> deserialize(yamlString: String?, typeReference: TypeReference<T>?): T {
        try {
            return OBJECT_MAPPER.readValue(yamlString, typeReference)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun deserialize(yamlString: String?): JsonNode {
        try {
            return OBJECT_MAPPER.readTree(yamlString)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    fun deserializeArray(stream: InputStream?): AutoCloseableIterator<JsonNode> {
        try {
            val parser = YAML_FACTORY.createParser(stream)

            // Check the first token
            check(parser.nextToken() == JsonToken.START_ARRAY) { "Expected content to be an array" }

            val iterator: Iterator<JsonNode> =
                object : AbstractIterator<JsonNode>() {
                    override fun computeNext(): JsonNode? {
                        try {
                            while (parser.nextToken() != JsonToken.END_ARRAY) {
                                return parser.readValueAsTree()
                            }
                        } catch (e: IOException) {
                            throw RuntimeException(e)
                        }
                        return endOfData()
                    }
                }

            return AutoCloseableIterators.fromIterator<JsonNode>(
                iterator,
                VoidCallable { parser.close() },
                null
            )
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    // todo (cgardens) - share this with Jsons if ever needed.
    /**
     * Creates a consumer that writes list items to the writer in a streaming fashion.
     *
     * @param writer writer to write to
     * @param <T> type of items being written
     * @return consumer that is able to write element to a list element by element. must be closed!
     * </T>
     */
    fun <T> listWriter(writer: Writer?): CloseableConsumer<T> {
        return YamlConsumer(writer, OBJECT_MAPPER)
    }

    class YamlConsumer<T>(writer: Writer?, objectMapper: ObjectMapper) : CloseableConsumer<T> {
        private val sequenceWriter: SequenceWriter =
            toRuntime(callable = { objectMapper.writer().writeValuesAsArray(writer) })

        override fun accept(t: T) {
            try {
                sequenceWriter.write(t)
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
        }

        @Throws(Exception::class)
        override fun close() {
            // closing the SequenceWriter closes the Writer that it wraps.
            sequenceWriter.close()
        }
    }
}
