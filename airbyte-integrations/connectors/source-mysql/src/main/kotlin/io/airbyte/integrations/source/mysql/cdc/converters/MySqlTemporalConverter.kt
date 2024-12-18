/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc.converters

import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.read.cdc.Converted
import io.airbyte.cdk.read.cdc.NoConversion
import io.airbyte.cdk.read.cdc.NullFallThrough
import io.airbyte.cdk.read.cdc.PartialConverter
import io.airbyte.cdk.read.cdc.RelationalColumnCustomConverter
import java.time.Duration
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZonedDateTime
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlTemporalConverter : RelationalColumnCustomConverter {

    override val debeziumPropertiesKey: String = "temporal"

    override val handlers: List<RelationalColumnCustomConverter.Handler> =
        listOf(datetimeHandler, dateHandler, timeHandler, timestampHandler)

    companion object {

        val datetimeHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = { it.typeName().equals("DATETIME", ignoreCase = true) },
                outputSchema = SchemaBuilder.string(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter {
                            if (it is LocalDateTime)
                                Converted(it.format(LocalDateTimeCodec.formatter))
                            else NoConversion
                        }
                    )
            )

        val dateHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = { it.typeName().equals("DATE", ignoreCase = true) },
                outputSchema = SchemaBuilder.string(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter {
                            if (it is LocalDate) Converted(it.format(LocalDateCodec.formatter))
                            else NoConversion
                        },
                    ),
            )

        val timeHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = { it.typeName().equals("TIME", ignoreCase = true) },
                outputSchema = SchemaBuilder.string(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter {
                            if (it is Duration)
                                Converted(
                                    LocalTime.MIDNIGHT.plus(it).format(LocalTimeCodec.formatter)
                                )
                            else NoConversion
                        },
                    ),
            )

        val timestampHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = { it.typeName().equals("TIMESTAMP", ignoreCase = true) },
                outputSchema = SchemaBuilder.string(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter {
                            if (it is ZonedDateTime)
                                Converted(
                                    it.toOffsetDateTime().format(OffsetDateTimeCodec.formatter)
                                )
                            else NoConversion
                        },
                    ),
            )
    }
}
