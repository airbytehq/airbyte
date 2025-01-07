/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.util.Properties
import org.apache.kafka.connect.data.Schema

/** Used by Debezium to transform record values into their expected format. */
interface RelationalColumnCustomConverter : CustomConverter<Schema, RelationalColumn> {

    /** A nice name for use in Debezium properties. */
    val debeziumPropertiesKey: String

    /** Fall-through list of handlers to try to match and register for each column. */
    val handlers: List<Handler>

    data class Handler(
        /** Predicate to match the column by. */
        val predicate: (RelationalColumn) -> Boolean,
        /** Schema of the output values. */
        val outputSchema: Schema,
        /** Partial conversion functions, applied in sequence until conversion occurs. */
        val partialConverters: List<PartialConverter>
    )

    override fun configure(props: Properties?) {}

    override fun converterFor(
        column: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<Schema>?
    ) {
        if (column == null || registration == null) {
            return
        }
        for (handler in handlers) {
            if (!handler.predicate(column)) continue
            val converter: CustomConverter.Converter =
                ConverterFactory(javaClass).build(column, handler.partialConverters)
            registration.register(handler.outputSchema, converter)
            return
        }
    }
}
