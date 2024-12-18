/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc.converters

import io.airbyte.cdk.read.cdc.Converted
import io.airbyte.cdk.read.cdc.NoConversion
import io.airbyte.cdk.read.cdc.PartialConverter
import io.airbyte.cdk.read.cdc.RelationalColumnCustomConverter
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlBooleanConverter : RelationalColumnCustomConverter {

    override val debeziumPropertiesKey: String = "boolean"
    override val handlers: List<RelationalColumnCustomConverter.Handler> =
        listOf(booleanHandler, tinyint1Handler)

    companion object {
        val booleanHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = { it.typeName().startsWith("BOOL", ignoreCase = true) },
                outputSchema = SchemaBuilder.bool(),
                partialConverters =
                    listOf(
                        PartialConverter {
                            when (it) {
                                null -> Converted(false)
                                is Boolean -> Converted(it)
                                else -> NoConversion
                            }
                        }
                    )
            )

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
                        PartialConverter {
                            when (it) {
                                null -> Converted(false)
                                is Number -> Converted(it != 0)
                                else -> NoConversion
                            }
                        }
                    )
            )
    }
}
