/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.*
import kotlin.IllegalStateException
import kotlin.Int
import kotlin.String
import kotlin.check
import kotlin.checkNotNull

object IncrementalUtils {
    private const val PROPERTIES = "properties"

    @JvmStatic
    fun getCursorField(stream: ConfiguredAirbyteStream): String {
        check(stream.cursorField.size != 0) {
            "No cursor field specified for stream attempting to do incremental."
        }
        check(stream.cursorField.size <= 1) { "Source does not support nested cursor fields." }
        return stream.cursorField[0]
    }

    @JvmStatic
    fun getCursorFieldOptional(stream: ConfiguredAirbyteStream): Optional<String> {
        return try {
            Optional.ofNullable(getCursorField(stream))
        } catch (e: IllegalStateException) {
            Optional.empty()
        }
    }

    @JvmStatic
    fun getCursorType(
        stream: ConfiguredAirbyteStream,
        cursorField: String?
    ): JsonSchemaPrimitiveUtil.JsonSchemaPrimitive? {
        checkNotNull(stream.stream.jsonSchema[PROPERTIES]) {
            String.format("No properties found in stream: %s.", stream.stream.name)
        }

        checkNotNull(stream.stream.jsonSchema[PROPERTIES][cursorField]) {
            String.format(
                "Could not find cursor field: %s in schema for stream: %s.",
                cursorField,
                stream.stream.name
            )
        }

        check(
            !(stream.stream.jsonSchema[PROPERTIES][cursorField]["type"] == null &&
                stream.stream.jsonSchema[PROPERTIES][cursorField]["\$ref"] == null)
        ) {
            String.format(
                "Could not find cursor type for field: %s in schema for stream: %s.",
                cursorField,
                stream.stream.name
            )
        }

        return if (stream.stream.jsonSchema[PROPERTIES][cursorField]["type"] == null) {
            JsonSchemaPrimitiveUtil.PRIMITIVE_TO_REFERENCE_BIMAP.inverse()[
                    stream.stream.jsonSchema[PROPERTIES][cursorField]["\$ref"].asText()]
        } else {
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.valueOf(
                stream.stream.jsonSchema[PROPERTIES][cursorField]["type"]
                    .asText()
                    .uppercase(Locale.getDefault())
            )
        }
    }

    /**
     * Comparator where if original is less than candidate then value less than 0, if greater than
     * candidate then value greater than 0, else 0
     *
     * @param original the first value to compare
     * @param candidate the second value to compare
     * @param type primitive type used to determine comparison
     * @return
     */
    @JvmStatic
    fun compareCursors(
        original: String?,
        candidate: String?,
        type: JsonSchemaPrimitiveUtil.JsonSchemaPrimitive?
    ): Int {
        if (original == null && candidate == null) {
            return 0
        }

        if (candidate == null) {
            return 1
        }

        if (original == null) {
            return -1
        }

        return when (type) {
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING_V1,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.DATE_V1,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.TIME_WITH_TIMEZONE_V1,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.TIME_WITHOUT_TIMEZONE_V1,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.TIMESTAMP_WITH_TIMEZONE_V1,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.TIMESTAMP_WITHOUT_TIMEZONE_V1 -> {
                original.compareTo(candidate)
            }
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NUMBER,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NUMBER_V1,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.INTEGER_V1 -> {
                // todo (cgardens) - handle big decimal. this is currently an overflow risk.
                original.toDouble().compareTo(candidate.toDouble())
            }
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.BOOLEAN,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.BOOLEAN_V1 -> {
                original.toBoolean().compareTo(candidate.toBoolean())
            }
            else ->
                throw IllegalStateException(
                    String.format("Cannot use field of type %s as a comparable", type)
                )
        }
    }
}
