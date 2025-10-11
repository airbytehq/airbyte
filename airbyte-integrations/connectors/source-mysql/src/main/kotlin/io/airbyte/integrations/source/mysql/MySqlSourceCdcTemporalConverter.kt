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
            DatetimeMillisHandler,
            DatetimeMicrosHandler,
            DateHandler,
            TimeHandler,
            TimestampHandler
        )
    /**
     * Handles zero-dates (e.g., '0000-00-00 00:00:00') which MySQL allows in NON-NULLABLE columns
     * but are invalid dates that JDBC drivers return as NULL. We are now converting those NULL
     * values to epoch (1970-01-01...) to match default value behavior and satisfy Debezium's
     * non-nullable schema constraints.
     */
    data object DatetimeMillisHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("DATETIME", ignoreCase = true) &&
                column.length().orElse(0) <= 3

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        val epoch = LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                        Converted(epoch.format(LocalDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
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

    data object DatetimeMicrosHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("DATETIME", ignoreCase = true) && column.length().orElse(0) > 3

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        val epoch = LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                        Converted(epoch.format(LocalDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
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

    data object DateHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("DATE", ignoreCase = true)

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        val epoch = LocalDate.ofEpochDay(0)
                        Converted(epoch.format(LocalDateCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
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
    /**
     * TIME supports '00:00:00' and it is considered valid, see
     * https://dev.mysql.com/doc/refman/8.0/en/time.html. If we get a null value from the server, it
     * means the TIME is invalid/corrupt and in that case we should return null.
     */
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
                PartialConverter {
                    if (it == null) {
                        val epoch = OffsetDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                        Converted(epoch.format(OffsetDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
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
