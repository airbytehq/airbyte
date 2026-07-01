/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import io.debezium.spi.converter.RelationalColumn
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
            DatetimeMillisHandler(),
            DatetimeMicrosHandler(),
            DateHandler(),
            TimeHandler,
            TimestampHandler
        )

    class DatetimeMillisHandler : RelationalColumnCustomConverter.Handler {

        private var currentColumn: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            val matches =
                column.typeName().equals("DATETIME", ignoreCase = true) &&
                    column.length().orElse(0) <= 3
            if (matches) {
                currentColumn = column
            }
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter>
            get() =
                listOf(
                    nonOptionalNullDateTimeConverter(currentColumn),
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
    }

    class DatetimeMicrosHandler : RelationalColumnCustomConverter.Handler {

        private var currentColumn: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            val matches =
                column.typeName().equals("DATETIME", ignoreCase = true) &&
                    column.length().orElse(0) > 3
            if (matches) {
                currentColumn = column
            }
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter>
            get() =
                listOf(
                    nonOptionalNullDateTimeConverter(currentColumn),
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
    }

    class DateHandler : RelationalColumnCustomConverter.Handler {

        private var currentColumn: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            val matches = column.typeName().equals("DATE", ignoreCase = true)
            if (matches) {
                currentColumn = column
            }
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter>
            get() =
                listOf(
                    nonOptionalNullDateConverter(currentColumn),
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
                )
    }

    companion object {
        private val epochDateTime: String =
            LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                .format(LocalDateTimeCodec.formatter)
        private val epochDate: String = LocalDate.EPOCH.format(LocalDateCodec.formatter)

        private fun nonOptionalNullDateTimeConverter(column: RelationalColumn?): PartialConverter =
            nonOptionalNullConverter(column, epochDateTime)

        private fun nonOptionalNullDateConverter(column: RelationalColumn?): PartialConverter =
            nonOptionalNullConverter(column, epochDate)

        private fun nonOptionalNullConverter(
            column: RelationalColumn?,
            fallback: String,
        ): PartialConverter = PartialConverter {
            if (it == null && column?.isOptional == false) {
                Converted(fallback)
            } else {
                NoConversion
            }
        }
    }

    data object TimeHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("TIME", ignoreCase = true)

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
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
            )
    }

    data object TimestampHandler : RelationalColumnCustomConverter.Handler {
        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("TIMESTAMP", ignoreCase = true)

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
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
            )
    }
}
