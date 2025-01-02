/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

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
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlSourceCdcTemporalConverter : RelationalColumnCustomConverter {

    override val debeziumPropertiesKey: String = "temporal"

    override val handlers: List<RelationalColumnCustomConverter.Handler> =
        listOf(
            datetimeMillisHandler,
            datetimeMicrosHandler,
            dateHandler,
            timeHandler,
            timestampHandler
        )

    companion object {

        val datetimeMillisHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = {
                    it.typeName().equals("DATETIME", ignoreCase = true) &&
                        it.length().orElse(0) <= 3
                },
                outputSchema = SchemaBuilder.string(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter {
                            if (it is LocalDateTime) {
                                Converted(it.format(LocalDateTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        },
                        PartialConverter {
                            // Required for default values.
                            if (it is Number) {
                                val delta: Duration = Duration.ofMillis(it.toLong())
                                val instant: Instant = Instant.EPOCH.plus(delta)
                                val localDateTime: LocalDateTime =
                                    LocalDateTime.ofInstant(instant, ZoneOffset.UTC)
                                Converted(localDateTime.format(LocalDateTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        }
                    )
            )

        val datetimeMicrosHandler =
            RelationalColumnCustomConverter.Handler(
                predicate = {
                    it.typeName().equals("DATETIME", ignoreCase = true) && it.length().orElse(0) > 3
                },
                outputSchema = SchemaBuilder.string(),
                partialConverters =
                    listOf(
                        NullFallThrough,
                        PartialConverter {
                            if (it is LocalDateTime) {
                                Converted(it.format(LocalDateTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        },
                        PartialConverter {
                            // Required for default values.
                            if (it is Number) {
                                val delta: Duration = Duration.of(it.toLong(), ChronoUnit.MICROS)
                                val instant: Instant = Instant.EPOCH.plus(delta)
                                val localDateTime: LocalDateTime =
                                    LocalDateTime.ofInstant(instant, ZoneOffset.UTC)
                                Converted(localDateTime.format(LocalDateTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
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
                            if (it is LocalDate) {
                                Converted(it.format(LocalDateCodec.formatter))
                            } else {
                                NoConversion
                            }
                        },
                        PartialConverter {
                            // Required for default values.
                            if (it is Number) {
                                val localDate: LocalDate = LocalDate.ofEpochDay(it.toLong())
                                Converted(localDate.format(LocalDateCodec.formatter))
                            } else {
                                NoConversion
                            }
                        }
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
                            if (it is Duration) {
                                val localTime: LocalTime = LocalTime.MIDNIGHT.plus(it)
                                Converted(localTime.format(LocalTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        },
                        PartialConverter {
                            // Required for default values.
                            if (it is Number) {
                                val delta: Duration = Duration.of(it.toLong(), ChronoUnit.MICROS)
                                val localTime: LocalTime = LocalTime.ofNanoOfDay(delta.toNanos())
                                Converted(localTime.format(LocalTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        }
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
                            if (it is ZonedDateTime) {
                                val offsetDateTime: OffsetDateTime = it.toOffsetDateTime()
                                Converted(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        },
                        PartialConverter {
                            // Required for default values.
                            if (it is String) {
                                val instant: Instant = Instant.parse(it)
                                val offsetDateTime: OffsetDateTime =
                                    OffsetDateTime.ofInstant(instant, ZoneOffset.UTC)
                                Converted(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                            } else {
                                NoConversion
                            }
                        }
                    ),
            )
    }
}
