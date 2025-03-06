/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.util.Properties
import org.apache.kafka.connect.data.SchemaBuilder

/** Used by Debezium to transform record values into their expected format. */
interface RelationalColumnCustomConverter : CustomConverter<SchemaBuilder, RelationalColumn> {

    /** A nice name for use in Debezium properties. */
    val debeziumPropertiesKey: String

    /** Fall-through list of handlers to try to match and register for each column. */
    val handlers: List<Handler>

    interface Handler {
        /** Predicate to match the column by. */
        fun matches(column: RelationalColumn): Boolean

        /** Schema of the output values. */
        fun outputSchemaBuilder(): SchemaBuilder

        /** Partial conversion functions, applied in sequence until conversion occurs. */
        val partialConverters: List<PartialConverter>
    }

    override fun configure(props: Properties?) {}

    override fun converterFor(
        column: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        if (column == null || registration == null) {
            return
        }
        val handler: Handler = handlers.find { it.matches(column) } ?: return
        val converter: CustomConverter.Converter =
            ConverterFactory(javaClass).build(column, handler.partialConverters)
        registration.register(handler.outputSchemaBuilder(), converter)
    }
}
