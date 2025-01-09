/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.debezium.spi.converter.ConvertedField
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean

/**
 * [PartialConverter] objects are used by [RelationalColumnCustomConverter.Handler] objects which to
 * define a sequence of conversion functions which work on a best-effort basis to convert a given
 * input value, provided by Debezium, into an output value which obeys the Airbyte Protocol.
 *
 * For example, a [PartialConverter] implementation for timestamps with time zones may attempt to
 * cast an input value as an [java.time.OffsetDateTime]. If the cast is unsuccessful the
 * [PartialConverter] will return [NoConversion], but if it's successful it will format it the way
 * Airbyte expects (ISO8601 with microsecond precision etc.) and wrap the result in a [Converted].
 */
fun interface PartialConverter {
    /** Attempts to convert the [input] to a valid result. */
    fun maybeConvert(input: Any?): PartialConverterResult
}

/** Output type of a [PartialConverter]. */
sealed interface PartialConverterResult

/** Returned by unsuccessful [PartialConverter] applications. */
data object NoConversion : PartialConverterResult

/** Returned by successful [PartialConverter] applications. */
data class Converted(val output: Any?) : PartialConverterResult

/**
 * Utility [PartialConverter] for dealing with null values when these are valid. This cuts down on
 * the boilerplate when defining subsequent [PartialConverter] implementations.
 */
object NullFallThrough : PartialConverter {
    override fun maybeConvert(input: Any?): PartialConverterResult =
        if (input == null) Converted(null) else NoConversion
}

/**
 * Utility [PartialConverter] for dealing with known default values. This cuts down on the
 * boilerplate when defining subsequent [PartialConverter] implementations.
 */
internal data class DefaultFallThrough(val defaultValue: Any?) : PartialConverter {
    override fun maybeConvert(input: Any?): PartialConverterResult =
        if (input == null) Converted(defaultValue) else NoConversion
}

/**
 * Factory class for generating [CustomConverter.Converter] instances for debezium given a list of
 * [PartialConverter]s.
 */
class ConverterFactory(val customConverterClass: Class<out CustomConverter<*, *>>) {
    private val log = KotlinLogging.logger {}

    /** Factory method for generating a [CustomConverter.Converter] for a [RelationalColumn]. */
    fun build(
        column: RelationalColumn,
        partialConverters: List<PartialConverter>
    ): CustomConverter.Converter {
        val noDefaultConverter = Converter(column, partialConverters, NoConversion)
        if (column.isOptional || !column.hasDefaultValue()) {
            log.info {
                "Building custom converter for" +
                    " column '${column.dataCollection()}.${column.name()}'" +
                    " of type '${column.typeName()}'."
            }
            return noDefaultConverter
        }
        val unconvertedDefaultValue: Any? = column.defaultValue()
        log.info {
            "Computing converted default value for" +
                " column '${column.dataCollection()}.${column.name()}'" +
                " of type '${column.typeName()}'" +
                " with unconverted default value '$unconvertedDefaultValue'."
        }
        val convertedDefaultValue: Any? = noDefaultConverter.convert(unconvertedDefaultValue)
        log.info {
            "Building custom converter for" +
                " column '${column.dataCollection()}.${column.name()}'" +
                " of type '${column.typeName()}'" +
                " with default value '$convertedDefaultValue'."
        }
        return Converter(column, partialConverters, Converted(convertedDefaultValue))
    }

    /** Implementation of [CustomConverter.Converter] used by [ConverterFactory]. */
    internal inner class Converter(
        private val convertedField: ConvertedField,
        private val partialConverters: List<PartialConverter>,
        private val defaultValue: PartialConverterResult,
    ) : CustomConverter.Converter {

        private val loggingFlag = AtomicBoolean()

        override fun convert(input: Any?): Any? {
            if (input == null && defaultValue is Converted) {
                return defaultValue.output
            }
            var cause: Throwable? = null
            for (converter in partialConverters) {
                val result: PartialConverterResult
                try {
                    result = converter.maybeConvert(input)
                } catch (e: Throwable) {
                    cause = e
                    break
                }
                when (result) {
                    NoConversion -> Unit
                    is Converted -> return result.output
                }
            }
            if (loggingFlag.compareAndSet(false, true)) {
                log.warn(cause) {
                    "Converter $customConverterClass" +
                        " for field ${convertedField.dataCollection()}.${convertedField.name()}" +
                        " cannot handle value '$input' of type ${input?.javaClass}."
                }
                log.warn { "Future similar warnings from $customConverterClass will be silenced." }
            }
            return null
        }
    }
}
