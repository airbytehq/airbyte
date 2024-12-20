/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.cdc.Converted
import io.airbyte.cdk.read.cdc.NoConversion
import io.airbyte.cdk.read.cdc.NullFallThrough
import io.airbyte.cdk.read.cdc.PartialConverter
import io.airbyte.cdk.read.cdc.RelationalColumnCustomConverter
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlSourceCdcBooleanConverter : RelationalColumnCustomConverter {

    override val debeziumPropertiesKey: String = "boolean"
    override val handlers: List<RelationalColumnCustomConverter.Handler> = listOf(tinyint1Handler)

    companion object {
        val tinyint1Handler =
            RelationalColumnCustomConverter.Handler(
                predicate = {
                    it.typeName().equals("TINYINT", ignoreCase = true) &&
                        it.length().isPresent &&
                        it.length().asInt == 1
                },
                outputSchema = SchemaBuilder.bool(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter { if (it is Number) Converted(it != 0) else NoConversion }
                    )
            )
    }
}
