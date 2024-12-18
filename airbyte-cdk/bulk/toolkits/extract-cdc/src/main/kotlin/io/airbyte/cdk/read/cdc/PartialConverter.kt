/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.debezium.spi.converter.ConvertedField
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean

fun interface PartialConverter {
    fun maybeConvert(input: Any?): PartialConverterResult
}

sealed interface PartialConverterResult

data object NoConversion : PartialConverterResult

data class Converted(val output: Any?) : PartialConverterResult

object NullFallThrough : PartialConverter {
    override fun maybeConvert(input: Any?): PartialConverterResult =
        if (input == null) Converted(null) else NoConversion
}

internal data class DefaultFallThrough(val defaultValue: Any?) : PartialConverter {
    override fun maybeConvert(input: Any?): PartialConverterResult =
        if (input == null) Converted(defaultValue) else NoConversion
}

class ConverterFactory(val customConverterClass: Class<out CustomConverter<*, *>>) {
    private val log = KotlinLogging.logger {}

    fun build(
        column: RelationalColumn,
        partialConverters: List<PartialConverter>
    ): CustomConverter.Converter =
        if (!column.isOptional && column.hasDefaultValue()) {
            val defaultValue: Any? = column.defaultValue()
            log.info {
                "Building custom converter for" +
                    " column '${column.dataCollection()}.${column.name()}'" +
                    " of type '${column.typeName()}'" +
                    " with default value '$defaultValue'."
            }
            Converter(column, listOf(DefaultFallThrough(defaultValue)) + partialConverters)
        } else {
            log.info {
                "Building custom converter for" +
                    " column '${column.dataCollection()}.${column.name()}'" +
                    " of type '${column.typeName()}'."
            }
            Converter(column, partialConverters)
        }

    inner class Converter(
        private val convertedField: ConvertedField,
        private val partialConverters: List<PartialConverter>,
    ) : CustomConverter.Converter {

        private val loggingFlag = AtomicBoolean()

        override fun convert(input: Any?): Any? {
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
