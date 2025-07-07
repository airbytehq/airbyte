/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.cdc.Converted
import io.airbyte.cdk.read.cdc.NoConversion
import io.airbyte.cdk.read.cdc.NullFallThrough
import io.airbyte.cdk.read.cdc.PartialConverter
import io.airbyte.cdk.read.cdc.RelationalColumnCustomConverter
import io.debezium.spi.converter.RelationalColumn
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlSourceCdcBooleanConverter : RelationalColumnCustomConverter {

    override val debeziumPropertiesKey: String = "boolean"
    override val handlers: List<RelationalColumnCustomConverter.Handler> = listOf(TinyInt1Handler)

    data object TinyInt1Handler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("TINYINT", ignoreCase = true) &&
                column.length().isPresent &&
                column.length().asInt == 1

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.bool()

        override val partialConverters: List<PartialConverter> =
            listOf(
                NullFallThrough,
                PartialConverter { if (it is Number) Converted(it != 0) else NoConversion }
            )
    }
}
