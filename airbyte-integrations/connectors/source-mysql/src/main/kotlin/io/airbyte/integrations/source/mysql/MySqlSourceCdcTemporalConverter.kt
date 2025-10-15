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
import io.github.oshai.kotlinlogging.KotlinLogging
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

    companion object {
         //Logs column null-handling behavior.
        fun logColumnNullHandling(
            customConverterHandlerName: String,
            column: RelationalColumn,
            matches: Boolean
        ) {
            val log = KotlinLogging.logger {}
            if (matches) {
                if (column.isOptional) {
                    log.info { "$customConverterHandlerName - Column '${column.name()}' is nullable, in case of zero-dates or NULL values, NULL will pass through" }
                } else {
                    log.warn { "$customConverterHandlerName - Column '${column.name()}' is NOT NULL, any NULL values (including zero-dates) will be converted to default epoch" }
                }
            }
        }
    }
    /**
     * Handling zero-dates (e.g., '0000-00-00 00:00:00'):
     * Zero-dates arrive from Debezium in two forms:
     * 1. As 0 (long)/epoch (1970-01-01...): typically for DEFAULT values or TIMESTAMP columns
     * 2. As NULL: for actual zero-date data in rows, which is handled based on column nullability:
     *    - NOT NULL columns: NULL is converted to epoch to prevent sync failures
     *    - Nullable columns: NULL passes through unchanged
     */
    data object DatetimeMillisHandler : RelationalColumnCustomConverter.Handler {
        private var column: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.column = column
            val matches = column.typeName().equals("DATETIME", ignoreCase = true) &&
                    column.length().orElse(0) <= 3
            logColumnNullHandling("DatetimeMillisHandler", column, matches)
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        if (column?.isOptional == true) {
                            Converted(null)
                        } else {
                            val epoch = LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                            Converted(epoch.format(LocalDateTimeCodec.formatter))
                        }
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
        private var column: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.column = column
            val matches =  column.typeName().equals("DATETIME", ignoreCase = true) && column.length().orElse(0) > 3
            logColumnNullHandling("DatetimeMicrosHandler", column, matches)
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        if (column?.isOptional == true) {
                            Converted(null)
                        } else {
                            val epoch = LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                            Converted(epoch.format(LocalDateTimeCodec.formatter))
                        }
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
        private var column: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.column = column
            val matches =  column.typeName().equals("DATE", ignoreCase = true)
            logColumnNullHandling("DateHandler", column, matches)
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        if (column?.isOptional == true) {
                            Converted(null)
                        } else {
                            val epoch = LocalDate.ofEpochDay(0)
                            Converted(epoch.format(LocalDateCodec.formatter))
                        }
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
        private var column: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.column = column
            val matches =  column.typeName().equals("TIMESTAMP", ignoreCase = true)
            logColumnNullHandling("TimestampHandler", column, matches)
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                PartialConverter {
                    if (it == null) {
                        if (column?.isOptional == true) {
                            Converted(null)
                        } else {
                            val epoch = OffsetDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                            Converted(epoch.format(OffsetDateTimeCodec.formatter))
                        }
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
