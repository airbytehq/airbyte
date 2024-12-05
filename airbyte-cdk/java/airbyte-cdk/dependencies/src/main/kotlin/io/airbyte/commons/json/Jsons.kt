/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.json

import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.core.StreamReadConstraints
import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter
import com.fasterxml.jackson.core.util.Separators
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.ObjectWriter
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.google.common.base.Charsets
import com.google.common.base.Preconditions
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.stream.MoreStreams
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.IOException
import java.util.*
import java.util.function.BiConsumer

private val LOGGER = KotlinLogging.logger {}

object Jsons {

    // allow jackson to deserialize anything under 100 MiB
    // (the default, at time of writing 2024-05-29, with jackson 2.15.2, is 20 MiB)
    private const val JSON_MAX_LENGTH = 100 * 1024 * 1024
    private val STREAM_READ_CONSTRAINTS =
        StreamReadConstraints.builder().maxStringLength(JSON_MAX_LENGTH).build()

    // Object Mapper is thread-safe
    private val OBJECT_MAPPER: ObjectMapper =
        MoreMappers.initMapper().also {
            it.factory.setStreamReadConstraints(STREAM_READ_CONSTRAINTS)
        }

    // sort of a hotfix; I don't know how bad the performance hit is so not turning this on by
    // default
    // at time of writing (2023-08-18) this is only used in tests, so we don't care.
    private val OBJECT_MAPPER_EXACT: ObjectMapper =
        MoreMappers.initMapper().also {
            it.enable(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS)
            it.factory.setStreamReadConstraints(STREAM_READ_CONSTRAINTS)
        }

    private val YAML_OBJECT_MAPPER: ObjectMapper = MoreMappers.initYamlMapper(YAMLFactory())
    private val OBJECT_WRITER: ObjectWriter = OBJECT_MAPPER.writer(JsonPrettyPrinter())

    @JvmStatic
    fun <T> serialize(`object`: T): String {
        try {
            return OBJECT_MAPPER.writeValueAsString(`object`)
        } catch (e: JsonProcessingException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun <T> deserialize(jsonString: String?, klass: Class<T>?): T {
        try {
            return OBJECT_MAPPER.readValue(jsonString, klass)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun <T> deserialize(jsonString: String?, valueTypeRef: TypeReference<T>?): T {
        try {
            return OBJECT_MAPPER.readValue(jsonString, valueTypeRef)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun <T> deserialize(file: File?, klass: Class<T>?): T {
        try {
            return OBJECT_MAPPER.readValue(file, klass)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun <T> deserialize(file: File?, valueTypeRef: TypeReference<T>?): T {
        try {
            return OBJECT_MAPPER.readValue(file, valueTypeRef)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun <T> convertValue(`object`: Any?, klass: Class<T>?): T {
        return OBJECT_MAPPER.convertValue(`object`, klass)
    }

    @JvmStatic
    fun deserialize(jsonString: String?): JsonNode {
        try {
            return OBJECT_MAPPER.readTree(jsonString)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun deserializeExact(jsonString: String?): JsonNode {
        try {
            return OBJECT_MAPPER_EXACT.readTree(jsonString)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun deserialize(jsonBytes: ByteArray?): JsonNode {
        try {
            return OBJECT_MAPPER.readTree(jsonBytes)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun deserializeExact(jsonBytes: ByteArray?): JsonNode {
        try {
            return OBJECT_MAPPER_EXACT.readTree(jsonBytes)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    // WARNING: This message throws bare exceptions on parse failure which might
    // leak sensitive data. Use obfuscateDeserializationException() to strip
    // the sensitive data before logging.
    @JvmStatic
    fun <T : Any> deserializeExactUnchecked(jsonString: String?, klass: Class<T>?): T {
        return OBJECT_MAPPER_EXACT.readValue(jsonString, klass)
    }

    @JvmStatic
    fun <T : Any> tryDeserialize(jsonString: String, klass: Class<T>): Optional<T> {
        return try {
            Optional.of(OBJECT_MAPPER.readValue(jsonString, klass))
        } catch (e: Throwable) {
            handleDeserThrowable(e)
        }
    }

    @JvmStatic
    fun <T : Any> tryDeserializeExact(jsonString: String?, klass: Class<T>?): Optional<T> {
        return try {
            Optional.of(OBJECT_MAPPER_EXACT.readValue(jsonString, klass))
        } catch (e: Throwable) {
            handleDeserThrowable(e)
        }
    }

    @JvmStatic
    fun tryDeserialize(jsonString: String?): Optional<JsonNode> {
        return try {
            Optional.of(OBJECT_MAPPER.readTree(jsonString))
        } catch (e: Throwable) {
            handleDeserThrowable(e)
        }
    }

    /**
     * This method does not generate deserialization warn log on why serialization failed. See also
     * [.tryDeserialize].
     *
     * @param jsonString
     * @return
     */
    @JvmStatic
    fun tryDeserializeWithoutWarn(jsonString: String?): Optional<JsonNode> {
        return try {
            Optional.of(OBJECT_MAPPER.readTree(jsonString))
        } catch (e: Throwable) {
            Optional.empty()
        }
    }

    @JvmStatic
    fun <T> jsonNode(`object`: T): JsonNode {
        return OBJECT_MAPPER.valueToTree(`object`)
    }

    @Throws(IOException::class)
    fun jsonNodeFromFile(file: File?): JsonNode {
        return YAML_OBJECT_MAPPER.readTree(file)
    }

    @JvmStatic
    fun emptyObject(): JsonNode {
        return jsonNode(emptyMap<Any, Any>())
    }

    @JvmStatic
    fun arrayNode(): ArrayNode {
        return OBJECT_MAPPER.createArrayNode()
    }

    @JvmStatic
    fun <T> `object`(jsonNode: JsonNode?, klass: Class<T>?): T? {
        return OBJECT_MAPPER.convertValue(jsonNode, klass)
    }

    @JvmStatic
    fun <T> `object`(jsonNode: JsonNode?, typeReference: TypeReference<T>): T? {
        return OBJECT_MAPPER.convertValue(jsonNode, typeReference)
    }

    fun <T : Any> tryObject(jsonNode: JsonNode?, klass: Class<T>?): Optional<T> {
        return try {
            Optional.of(OBJECT_MAPPER.convertValue(jsonNode, klass))
        } catch (e: Exception) {
            Optional.empty()
        }
    }

    fun <T : Any> tryObject(jsonNode: JsonNode?, typeReference: TypeReference<T>?): Optional<T> {
        return try {
            Optional.of(OBJECT_MAPPER.convertValue(jsonNode, typeReference))
        } catch (e: Exception) {
            Optional.empty()
        }
    }

    @JvmStatic
    fun <T : Any> clone(o: T): T {
        return deserialize(serialize(o), o::class.java)
    }

    fun toBytes(jsonNode: JsonNode): ByteArray {
        return serialize(jsonNode).toByteArray(Charsets.UTF_8)
    }

    /**
     * Use string length as an estimation for byte size, because all ASCII characters are one byte
     * long in UTF-8, and ASCII characters cover most of the use cases. To be more precise, we can
     * convert the string to byte[] and use the length of the byte[]. However, this conversion is
     * expensive in memory consumption. Given that the byte size of the serialized JSON is already
     * an estimation of the actual size of the JSON object, using a cheap operation seems an
     * acceptable compromise.
     */
    @JvmStatic
    fun getEstimatedByteSize(jsonNode: JsonNode): Int {
        return serialize(jsonNode).length
    }

    fun keys(jsonNode: JsonNode): Set<String> {
        return if (jsonNode.isObject) {
            `object`(jsonNode, object : TypeReference<Map<String, Any>>() {})!!.keys
        } else {
            HashSet()
        }
    }

    fun children(jsonNode: JsonNode): List<JsonNode> {
        return MoreStreams.toStream(jsonNode.elements()).toList()
    }

    fun toPrettyString(jsonNode: JsonNode?): String {
        try {
            return OBJECT_WRITER.writeValueAsString(jsonNode) + "\n"
        } catch (e: JsonProcessingException) {
            throw RuntimeException(e)
        }
    }

    fun navigateTo(node: JsonNode, keys: List<String>): JsonNode {
        var targetNode = node
        for (key in keys) {
            targetNode = targetNode[key]
        }
        return targetNode
    }

    fun replaceNestedValue(json: JsonNode, keys: List<String>, replacement: JsonNode?) {
        replaceNested(json, keys) { node: ObjectNode, finalKey: String ->
            node.replace(finalKey, replacement)
        }
    }

    fun replaceNestedString(json: JsonNode, keys: List<String>, replacement: String?) {
        replaceNested(json, keys) { node: ObjectNode, finalKey: String ->
            node.put(finalKey, replacement)
        }
    }

    fun replaceNestedInt(json: JsonNode, keys: List<String>, replacement: Int) {
        replaceNested(json, keys) { node: ObjectNode, finalKey: String ->
            node.put(finalKey, replacement)
        }
    }

    private fun replaceNested(
        json: JsonNode,
        keys: List<String>,
        typedReplacement: BiConsumer<ObjectNode, String>
    ) {
        Preconditions.checkArgument(!keys.isEmpty(), "Must pass at least one key")
        val nodeContainingFinalKey = navigateTo(json, keys.subList(0, keys.size - 1))
        typedReplacement.accept(nodeContainingFinalKey as ObjectNode, keys[keys.size - 1])
    }

    fun getOptional(json: JsonNode?, vararg keys: String): Optional<JsonNode> {
        return getOptional(json, Arrays.asList(*keys))
    }

    fun getOptional(json: JsonNode?, keys: List<String>): Optional<JsonNode> {
        var retVal = json
        for (key in keys) {
            if (retVal == null) {
                return Optional.empty()
            }

            retVal = retVal[key]
        }

        return Optional.ofNullable(retVal)
    }

    fun getStringOrNull(json: JsonNode?, vararg keys: String): String? {
        return getStringOrNull(json, Arrays.asList(*keys))
    }

    fun getStringOrNull(json: JsonNode?, keys: List<String>): String? {
        val optional = getOptional(json, keys)
        return optional.map { obj: JsonNode -> obj.asText() }.orElse(null)
    }

    fun getIntOrZero(json: JsonNode?, vararg keys: String): Int {
        return getIntOrZero(json, Arrays.asList(*keys))
    }

    fun getIntOrZero(json: JsonNode?, keys: List<String>): Int {
        val optional = getOptional(json, keys)
        return optional.map { obj: JsonNode -> obj.asInt() }.orElse(0)
    }

    /**
     * Flattens an ObjectNode, or dumps it into a {null: value} map if it's not an object. When
     * applyFlattenToArray is true, each element in the array will be one entry in the returned map.
     * This behavior is used in the Redshift SUPER type. When it is false, the whole array will be
     * one entry. This is used in the JobTracker.
     */
    /**
     * Flattens an ObjectNode, or dumps it into a {null: value} map if it's not an object. New usage
     * of this function is best to explicitly declare the intended array mode. This version is
     * provided for backward compatibility.
     */
    @JvmOverloads
    @JvmStatic
    fun flatten(node: JsonNode, applyFlattenToArray: Boolean = false): Map<String?, Any> {
        if (node.isObject) {
            val output: MutableMap<String, Any> = HashMap()
            val it = node.fields()
            while (it.hasNext()) {
                val entry = it.next()
                val field = entry.key
                val value = entry.value
                mergeMaps(output, field, flatten(value, applyFlattenToArray))
            }
            return output.toMap()
        } else if (node.isArray && applyFlattenToArray) {
            val output: MutableMap<String, Any> = HashMap()
            val arrayLen = node.size()
            for (i in 0 until arrayLen) {
                val field = String.format("[%d]", i)
                val value = node[i]
                mergeMaps(output, field, flatten(value, applyFlattenToArray))
            }
            return output.toMap()
        } else {
            val value: Any =
                if (node.isBoolean) {
                    node.asBoolean()
                } else if (node.isLong) {
                    node.asLong()
                } else if (node.isInt) {
                    node.asInt()
                } else if (node.isDouble) {
                    node.asDouble()
                } else if (node.isValueNode && !node.isNull) {
                    node.asText()
                } else {
                    // Fallback handling for e.g. arrays
                    node.toString()
                }
            return Collections.singletonMap(null, value)
        }
    }

    /**
     * Prepend all keys in subMap with prefix, then merge that map into originalMap.
     *
     * If subMap contains a null key, then instead it is replaced with prefix. I.e. {null: value} is
     * treated as {prefix: value} when merging into originalMap.
     */
    fun mergeMaps(originalMap: MutableMap<String, Any>, prefix: String, subMap: Map<String?, Any>) {
        originalMap.putAll(
            subMap.mapKeys toMap@{
                val key = it.key
                if (key != null) {
                    return@toMap "$prefix.$key"
                } else {
                    return@toMap prefix
                }
            },
        )
    }

    fun deserializeToStringMap(json: JsonNode?): Map<String, String> {
        return OBJECT_MAPPER.convertValue(json, object : TypeReference<Map<String, String>>() {})
    }

    /**
     * Simple utility method to log a semi-useful message when deserialization fails. Intentionally
     * don't log the actual exception object, because it probably contains some/all of the
     * inputString (e.g. `<snip...>[Source: (String)"{"foo": "bar"; line: 1, column: 13]`). Logging
     * the class name can at least help narrow down the problem, without leaking
     * potentially-sensitive information. </snip...>
     */
    private fun <T : Any> handleDeserThrowable(throwable: Throwable): Optional<T> {
        val obfuscated = obfuscateDeserializationException(throwable)
        LOGGER.warn { "Failed to deserialize json due to $obfuscated" }
        return Optional.empty()
    }

    /**
     * Build a stacktrace from the given throwable, enabling us to log or rethrow without leaking
     * sensitive information in the exception message (which would be exposed with eg,
     * ExceptionUtils.getStackTrace(t).)
     */
    fun obfuscateDeserializationException(throwable: Throwable): String {
        var t: Throwable = throwable
        val sb = StringBuilder()
        sb.append(t.javaClass)
        for (traceElement in t.stackTrace) {
            sb.append("\n\tat ")
            sb.append(traceElement.toString())
        }
        while (t.cause != null) {
            t = t.cause!!
            sb.append("\nCaused by ")
            sb.append(t.javaClass)
            for (traceElement in t.stackTrace) {
                sb.append("\n\tat ")
                sb.append(traceElement.toString())
            }
        }
        return sb.toString()
    }

    /**
     * By the Jackson DefaultPrettyPrinter prints objects with an extra space as follows: {"name" :
     * "airbyte"}. We prefer {"name": "airbyte"}.
     */
    private class JsonPrettyPrinter : DefaultPrettyPrinter() {
        // this method has to be overridden because in the superclass it checks that it is an
        // instance of
        // DefaultPrettyPrinter (which is no longer the case in this inherited class).
        override fun createInstance(): DefaultPrettyPrinter {
            return DefaultPrettyPrinter(this)
        }

        // override the method that inserts the extra space.
        override fun withSeparators(separators: Separators): DefaultPrettyPrinter {
            _separators = separators
            _objectFieldValueSeparatorWithSpaces =
                separators.objectFieldValueSeparator.toString() + " "
            return this
        }
    }
}
