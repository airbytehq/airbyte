/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField
import java.util.Properties
import org.apache.kafka.connect.data.SchemaBuilder

/** Used by Debezium to transform record values into their expected format. */
class OracleAirbyteCustomConverter : CustomConverter<SchemaBuilder, RelationalColumn> {
    private val log = KotlinLogging.logger {}

    override fun configure(props: Properties?) {}

    override fun converterFor(
        column: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder>?
    ) {
        if (column == null || registration == null) {
            return
        }
        if (dateRegex.isPrefixOfTypeNameOf(column)) {
            registration.register(SchemaBuilder.string(), column.converter(::convertDate))
            return
        }
        if (timestampTzRegex.isPrefixOfTypeNameOf(column)) {
            registration.register(SchemaBuilder.string(), column.converter(::convertOffsetDateTime))
            return
        }
        if (timestampRegex.isPrefixOfTypeNameOf(column)) {
            registration.register(SchemaBuilder.string(), column.converter(::convertLocalDateTime))
            return
        }
        if (intervalYearToMonthRegex.isPrefixOfTypeNameOf(column)) {
            registration.register(
                SchemaBuilder.string(),
                column.converter(::convertIntervalYearMonth)
            )
            return
        }
        if (intervalDayToSecondRegex.isPrefixOfTypeNameOf(column)) {
            registration.register(
                SchemaBuilder.string(),
                column.converter(::convertIntervalDaySecond)
            )
            return
        }
    }

    private fun <T> RelationalColumn.converter(fn: (Any) -> T): CustomConverter.Converter {
        val column: RelationalColumn = this
        val fallbackValue: Any? =
            if (!column.isOptional && column.hasDefaultValue()) column.defaultValue() else null
        log.info {
            "Registering custom converter for " +
                "column '${column.dataCollection()}.${column.name()}' " +
                "of type '${column.typeName()}' " +
                "with default value '$fallbackValue'."
        }
        return CustomConverter.Converter { x -> if (x == null) fallbackValue else fn(x) }
    }

    companion object {

        private val dateRegex: Regex = "DATE".toRegex(RegexOption.IGNORE_CASE)

        private val timestampRegex: Regex = "TIMESTAMP.*".toRegex(RegexOption.IGNORE_CASE)

        private val timestampTzRegex: Regex =
            "TIMESTAMP.* WITH TIME ZONE|TIMESTAMP.* WITH TZ".toRegex(RegexOption.IGNORE_CASE)

        private val intervalYearToMonthRegex: Regex =
            "INTERVAL YEAR.* TO MONTH".toRegex(RegexOption.IGNORE_CASE)

        private val intervalDayToSecondRegex: Regex =
            "INTERVAL DAY.* TO SECOND".toRegex(RegexOption.IGNORE_CASE)

        private fun Regex.isPrefixOfTypeNameOf(column: RelationalColumn?): Boolean =
            column?.typeName()?.let(::find)?.range?.first == 0

        @JvmStatic
        private fun convertDate(x: Any): String {
            val match: MatchResult = toDateRegex.matchEntire(x.toString()) ?: return x.toString()
            val (date: String) = match.destructured
            val localDateTime: LocalDateTime = LocalDateTime.parse(date, dateFormatter)
            return localDateTime.format(LocalDateTimeCodec.formatter)
        }

        private val toDateRegex: Regex =
            "TO_DATE\\('(.+)', '.+'\\)".toRegex(RegexOption.IGNORE_CASE)

        private val dateFormatter: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendOptional(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
                .appendOptional(DateTimeFormatter.ofPattern("yyyy-MM-dd"))
                .toFormatter()

        @JvmStatic
        private fun convertLocalDateTime(x: Any): String {
            val match: MatchResult =
                toTimestampRegex.matchEntire(x.toString()) ?: return x.toString()
            val (timestamp: String) = match.destructured
            val localDateTime: LocalDateTime = LocalDateTime.parse(timestamp, timestampFormatter)
            return localDateTime.format(LocalDateTimeCodec.formatter)
        }

        private val toTimestampRegex: Regex =
            "TO_TIMESTAMP\\('(.+)'\\)".toRegex(RegexOption.IGNORE_CASE)

        private val timestampFormatter: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd HH:mm:ss")
                .optionalStart()
                .appendFraction(
                    ChronoField.NANO_OF_SECOND,
                    1,
                    9,
                    true
                ) // Min 1, max 9 fractional digits
                .optionalEnd()
                .toFormatter()

        @JvmStatic
        private fun convertOffsetDateTime(x: Any): String {
            val match: MatchResult =
                toTimestampTzRegex.matchEntire(x.toString()) ?: return x.toString()
            val (timestampTz: String) = match.destructured
            val offsetDateTime: OffsetDateTime =
                OffsetDateTime.parse(timestampTz, timestampTzFormatter)
            return offsetDateTime.format(OffsetDateTimeCodec.formatter)
        }

        private val toTimestampTzRegex: Regex =
            "TO_TIMESTAMP_TZ\\('(.+)'\\)".toRegex(RegexOption.IGNORE_CASE)

        private val timestampTzFormatter: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd HH:mm:ss")
                .optionalStart()
                .appendFraction(
                    ChronoField.NANO_OF_SECOND,
                    1,
                    9,
                    true
                ) // Min 1, max 9 fractional digits
                .optionalEnd()
                .appendPattern(" XXX")
                .toFormatter()

        @JvmStatic
        private fun convertIntervalYearMonth(x: Any): String {
            val match: MatchResult =
                toYMIntervalRegex.matchEntire(x.toString()) ?: return x.toString()
            val (y: String, m: String) = match.destructured
            return "${y.toInt()}-${m.toInt()}"
        }

        private val toYMIntervalRegex: Regex =
            "TO_YMINTERVAL\\('([+-]?[0-9]+)-([0-9]+)'\\)".toRegex(RegexOption.IGNORE_CASE)

        @JvmStatic
        private fun convertIntervalDaySecond(x: Any?): String {
            val match: MatchResult =
                toDSIntervalRegex.matchEntire(x.toString()) ?: return x.toString()
            val (d: String, h: String, m: String, s: String, millis: String) = match.destructured
            val millisOrZero: String = millis.takeUnless { it.isEmpty() } ?: "0"
            return "${d.toInt()} ${h.toInt()}:${m.toInt()}:${s.toInt()}.$millisOrZero"
        }

        private val toDSIntervalRegex: Regex =
            "TO_DSINTERVAL\\('([+-]?[0-9]+) ([0-9]+):([0-9]+):([0-9]+)(?:\\.([0-9]+))?'\\)".toRegex(
                RegexOption.IGNORE_CASE
            )
    }
}
