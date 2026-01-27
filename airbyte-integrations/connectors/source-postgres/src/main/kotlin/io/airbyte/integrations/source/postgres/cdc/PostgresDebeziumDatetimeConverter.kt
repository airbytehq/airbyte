/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter.convertToDate
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter.convertToTime
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter.convertToTimeWithTimezone
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter.convertToTimestamp
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter.convertToTimestampWithTimezone
import io.debezium.connector.postgresql.PostgresValueConverter
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.debezium.time.Conversions
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.nio.charset.StandardCharsets
import java.sql.SQLException
import java.time.LocalDate
import java.time.LocalTime
import java.time.OffsetTime
import java.time.format.DateTimeFormatter
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.function.Consumer
import java.util.stream.Collectors
import kotlin.math.abs
import org.apache.kafka.connect.data.Schema
import org.apache.kafka.connect.data.SchemaBuilder
import org.postgresql.jdbc.PgArray
import org.postgresql.util.PGInterval

class PostgresDebeziumDatetimeConverter : CustomConverter<SchemaBuilder?, RelationalColumn?> {
    private val DATE_TYPES =
        arrayOf<String?>("DATE", "TIME", "TIMETZ", "INTERVAL", "TIMESTAMP", "TIMESTAMPTZ")
    private val BIT_TYPES = arrayOf<String?>("BIT", "VARBIT")
    private val MONEY_ITEM_TYPE = arrayOf<String?>("MONEY")
    private val GEOMETRICS_TYPES =
        arrayOf<String?>("BOX", "CIRCLE", "LINE", "LSEG", "POINT", "POLYGON", "PATH")
    private val TEXT_TYPES =
        arrayOf<String?>(
            "VARCHAR",
            "VARBINARY",
            "BLOB",
            "TEXT",
            "LONGTEXT",
            "TINYTEXT",
            "MEDIUMTEXT",
            "INVENTORY_ITEM",
            "TSVECTOR",
            "TSQUERY",
            "PG_LSN",
        )
    private val NUMERIC_TYPES = arrayOf<String?>("NUMERIC", "DECIMAL")
    private val ARRAY_TYPES =
        arrayOf<String?>(
            "_NAME",
            "_NUMERIC",
            "_BYTEA",
            "_MONEY",
            "_BIT",
            "_DATE",
            "_TIME",
            "_TIMETZ",
            "_TIMESTAMP",
            "_TIMESTAMPTZ",
        )
    private val BYTEA_TYPE = "BYTEA"

    // Debezium is manually setting the variable scale decimal length (precision)
    // of numeric_array columns to 131089 if not specified. e.g: NUMERIC vs NUMERIC(38,0)
    // https://github.com/debezium/debezium/blob/main/debezium-connector-postgres/src/main/java/io/debezium/connector/postgresql/PostgresValueConverter.java#L113
    private val VARIABLE_SCALE_DECIMAL_LENGTH = 131089

    override fun configure(props: Properties?) {}

    override fun converterFor(
        field: RelationalColumn?,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>?
    ) {
        if (field == null || registration == null) return
        if (
            Arrays.stream<String?>(DATE_TYPES).anyMatch { s: String? ->
                s.equals(field.typeName(), ignoreCase = true)
            }
        ) {
            registerDate(field, registration)
        } else if (
            Arrays.stream<String?>(TEXT_TYPES).anyMatch { s: String? ->
                s.equals(field.typeName(), ignoreCase = true)
            } ||
                Arrays.stream<String?>(GEOMETRICS_TYPES).anyMatch { s: String? ->
                    s.equals(field.typeName(), ignoreCase = true)
                } ||
                Arrays.stream<String?>(BIT_TYPES).anyMatch { s: String? ->
                    s.equals(field.typeName(), ignoreCase = true)
                }
        ) {
            registerText(field, registration)
        } else if (
            Arrays.stream<String?>(MONEY_ITEM_TYPE).anyMatch { s: String? ->
                s.equals(field.typeName(), ignoreCase = true)
            }
        ) {
            registerMoney(field, registration)
        } else if (BYTEA_TYPE.equals(field.typeName(), ignoreCase = true)) {
            registerBytea(field, registration)
        } else if (
            Arrays.stream<String?>(NUMERIC_TYPES).anyMatch { s: String? ->
                s.equals(field.typeName(), ignoreCase = true)
            }
        ) {
            registerNumber(field, registration)
        } else if (
            Arrays.stream<String?>(ARRAY_TYPES).anyMatch { s: String? ->
                s.equals(field.typeName(), ignoreCase = true)
            }
        ) {
            registerArray(field, registration)
        }
    }

    private fun registerArray(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>
    ) {
        val fieldType = field.typeName().uppercase(Locale.getDefault())
        val arraySchema =
            when (fieldType) {
                "_NUMERIC" -> {
                    // If a numeric_array column does not have variable precision AND scale is 0
                    // then we know the precision and scale are purposefully chosen
                    if (
                        numericArrayColumnPrecisionIsNotVariable(field) &&
                            field.scale().orElse(0) == 0
                    ) {
                        SchemaBuilder.array(Schema.OPTIONAL_INT64_SCHEMA).optional()
                    } else {
                        SchemaBuilder.array(Schema.OPTIONAL_FLOAT64_SCHEMA).optional()
                    }
                }
                "_MONEY" -> SchemaBuilder.array(Schema.OPTIONAL_FLOAT64_SCHEMA).optional()
                "_NAME",
                "_DATE",
                "_TIME",
                "_TIMESTAMP",
                "_TIMESTAMPTZ",
                "_TIMETZ",
                "_BYTEA" ->
                    SchemaBuilder.array(
                            Schema.OPTIONAL_STRING_SCHEMA,
                        )
                        .optional()
                "_BIT" -> SchemaBuilder.array(Schema.OPTIONAL_BOOLEAN_SCHEMA).optional()
                else -> SchemaBuilder.array(Schema.OPTIONAL_STRING_SCHEMA).optional()
            }
        registration.register(
            arraySchema,
            CustomConverter.Converter { x: Any? -> convertArray(x, field) },
        )
    }

    private fun registerNumber(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>
    ) {
        registration.register(
            SchemaBuilder.string().optional(),
            CustomConverter.Converter { x: Any? ->
                if (x == null) {
                    val defaultValue: Any? = convertDefaultValue(field)
                    return@Converter if (defaultValue == null) null
                    else
                        getNumberConvertedValue(
                            defaultValue,
                        )
                }
                getNumberConvertedValue(x)
            },
        )
    }

    private fun getNumberConvertedValue(x: Any): String {
        // Bad solution
        // We applied a solution like this for several reasons:
        // 1. Regarding #13608, CDC and nor-CDC data output format should be the same.
        // 2. In the non-CDC mode 'decimal' and 'numeric' values are put to JSON node as BigDecimal
        // value.
        // According to Jackson Object mapper configuration, all trailing zeros are omitted and
        // numbers with decimal places are deserialized with exponent. (e.g. 1234567890.1234567
        // would
        // be deserialized as 1.2345678901234567E9).
        // 3. In the CDC mode 'decimal' and 'numeric' values are deserialized as a regular number
        // (e.g.
        // 1234567890.1234567 would be deserialized as 1234567890.1234567). Numbers without
        // decimal places (e.g 1, 24, 354) are represented with trailing zero (e.g 1.0, 24.0,
        // 354.0).
        // One of solution to align deserialization for these 2 modes is setting
        // DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS as true for ObjectMapper. But this
        // breaks
        // deserialization for other data-types.
        // A worked solution was to keep deserialization for non-CDC mode as it is and change it for
        // CDC
        // one.
        // The code below strips trailing zeros for integer numbers and represents number with
        // exponent
        // if this number has decimals point.
        val doubleValue = x.toString().toDouble()
        val valueWithTruncatedZero =
            BigDecimal.valueOf(doubleValue).stripTrailingZeros().toPlainString()
        return if (valueWithTruncatedZero.contains(".")) doubleValue.toString()
        else valueWithTruncatedZero
    }

    private fun registerBytea(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>
    ) {
        registration.register(
            SchemaBuilder.string().optional(),
            CustomConverter.Converter { x: Any? ->
                if (x == null) {
                    val defaultValue: Any? = convertDefaultValue(field)
                    return@Converter if (defaultValue == null) null
                    else
                        "\\x" +
                            encodeHexString(
                                defaultValue as ByteArray,
                            )
                }
                "\\x" + encodeHexString(x as ByteArray)
            },
        )
    }

    private fun registerText(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>
    ) {
        registration.register(
            SchemaBuilder.string().optional(),
            CustomConverter.Converter { x: Any? ->
                if (x == null) {
                    val defaultValue: Any? = convertDefaultValue(field)
                    return@Converter if (defaultValue == null) null
                    else
                        getTextConvertedValue(
                            defaultValue,
                        )
                }
                getTextConvertedValue(x)
            },
        )
    }

    private fun getTextConvertedValue(x: Any): String? {
        if (x is ByteArray) {
            return String(x, StandardCharsets.UTF_8)
        } else {
            return x.toString()
        }
    }

    private fun convertArray(x: Any?, field: RelationalColumn): Any? {
        if (x == null) {
            val defaultValue: Any? = convertDefaultValue(field)
            return if (defaultValue == null) null else getArrayConvertedValue(field, defaultValue)
        }
        return getArrayConvertedValue(field, x)
    }

    private fun getArrayConvertedValue(field: RelationalColumn, x: Any): Any {
        val fieldType = field.typeName().uppercase(Locale.getDefault())
        when (fieldType) {
            "_MONEY" -> {
                // PgArray.getArray() trying to convert to Double instead of PgMoney
                // due to incorrect type mapping in the postgres driver
                // https://github.com/pgjdbc/pgjdbc/blob/d5ed52ef391670e83ae5265af2f7301c615ce4ca/pgjdbc/src/main/java/org/postgresql/jdbc/TypeInfoCache.java#L88
                // and throws an exception, so a custom implementation of converting to String is
                // used to get the
                // value as is
                val nativeMoneyValue = (x as PgArray).toString()
                val substringM =
                    Objects.requireNonNull<String?>(nativeMoneyValue)
                        .substring(1, nativeMoneyValue!!.length - 1)
                val currency = substringM.get(0)
                val regex = "\\" + currency
                val myListM: MutableList<String?> =
                    ArrayList<String?>(
                        Arrays.asList<String>(
                            *substringM
                                .split(regex.toRegex())
                                .dropLastWhile { it.isEmpty() }
                                .toTypedArray(),
                        ),
                    )
                return myListM
                    .stream() // since the separator is the currency sign, all extra characters must
                    // be removed except for numbers
                    // and dots
                    .map<String?> { `val`: String? -> `val`!!.replace("[^\\d.]".toRegex(), "") }
                    .filter { money: String? -> !money!!.isEmpty() }
                    .map<Double?> { s: String? -> s?.toDouble() }
                    .collect(Collectors.toList())
            }
            "_NUMERIC" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map { value: Any? ->
                        if (value == null) {
                            return@map null
                        } else {
                            if (
                                numericArrayColumnPrecisionIsNotVariable(field) &&
                                    field.scale().orElse(0) == 0
                            ) {
                                return@map value.toString().toLong()
                            } else {
                                return@map value.toString().toDouble()
                            }
                        }
                    }
                    .collect(Collectors.toList())
            "_TIME" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<String> { value: Any? ->
                        if (value == null) null else convertToTime(value)
                    }
                    .collect(
                        Collectors.toList(),
                    )
            "_DATE" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<String> { value: Any? ->
                        if (value == null) null else convertToDate(value)
                    }
                    .collect(
                        Collectors.toList(),
                    )
            "_TIMESTAMP" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<String> { value: Any? ->
                        if (value == null) null else convertToTimestamp(value)
                    }
                    .collect(
                        Collectors.toList(),
                    )
            "_TIMESTAMPTZ" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<String> { value: Any? ->
                        if (value == null) null else convertToTimestampWithTimezone(value)
                    }
                    .collect(
                        Collectors.toList(),
                    )
            "_TIMETZ" -> {
                val timetzArr: MutableList<String?> = ArrayList<String?>()
                val nativeValue = (x as PgArray).toString()
                val substring =
                    Objects.requireNonNull<String?>(nativeValue)
                        .substring(1, nativeValue!!.length - 1)
                val times: MutableList<String?> =
                    ArrayList<String?>(
                        Arrays.asList<String>(
                            *substring
                                .split(",".toRegex())
                                .dropLastWhile { it.isEmpty() }
                                .toTypedArray(),
                        ),
                    )
                val format = DateTimeFormatter.ofPattern("HH:mm:ss[.SSSSSS]X")

                times.forEach(
                    Consumer { s: String? ->
                        if (s.equals("NULL", ignoreCase = true)) {
                            timetzArr.add(null)
                        } else {
                            val parsed = OffsetTime.parse(s, format)
                            timetzArr.add(convertToTimeWithTimezone(parsed))
                        }
                    },
                )
                return timetzArr
            }
            "_BYTEA" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<String?> { value: Any? ->
                        Base64.getEncoder().encodeToString(value as ByteArray?)
                    }
                    .collect(
                        Collectors.toList(),
                    )
            "_BIT" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<Boolean?> { value: Any? -> value as Boolean? }
                    .collect(
                        Collectors.toList(),
                    )
            "_NAME" ->
                return Arrays.stream<Any?>(getArray(x))
                    .map<String?> { value: Any? -> value as String? }
                    .collect(
                        Collectors.toList(),
                    )
            else -> throw RuntimeException("Unknown array type detected " + fieldType)
        }
    }

    @Suppress("UNCHECKED_CAST")
    private fun getArray(x: Any): Array<Any?>? {
        try {
            return (x as PgArray).array as Array<Any?>?
        } catch (e: SQLException) {
            log.error { "Failed to convert PgArray:$e" }
            throw RuntimeException(e)
        }
    }

    private fun getTimePrecision(field: RelationalColumn): Int {
        return field.scale().orElse(-1)
    }

    private val POSITIVE_INFINITY_VALUE = "Infinity"
    private val NEGATIVE_INFINITY_VALUE = "-Infinity"

    // Ref :
    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-temporal-types
    private fun registerDate(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>
    ) {
        registration.register(
            SchemaBuilder.string().optional(),
            CustomConverter.Converter { x: Any? ->
                if (x == null) {
                    val defaultValue: Any? = convertDefaultValue(field)
                    return@Converter if (defaultValue == null) null
                    else
                        getDateConvertedValue(
                            field,
                            defaultValue,
                        )
                }
                getDateConvertedValue(field, x)
            },
        )
    }

    private fun getDateConvertedValue(field: RelationalColumn, x: Any): String {
        when (field.typeName().uppercase()) {
            "TIMETZ" -> return convertToTimeWithTimezone(x)
            "TIMESTAMPTZ" -> {
                if (x == PostgresValueConverter.NEGATIVE_INFINITY_OFFSET_DATE_TIME) {
                    return NEGATIVE_INFINITY_VALUE
                }
                if (x == PostgresValueConverter.POSITIVE_INFINITY_OFFSET_DATE_TIME) {
                    return POSITIVE_INFINITY_VALUE
                }
                return convertToTimestampWithTimezone(x)
            }
            "TIMESTAMP" -> {
                if (x == PostgresValueConverter.NEGATIVE_INFINITY_INSTANT) {
                    return NEGATIVE_INFINITY_VALUE
                }
                if (x == PostgresValueConverter.POSITIVE_INFINITY_INSTANT) {
                    return POSITIVE_INFINITY_VALUE
                }
                if (x is Long) {
                    if (getTimePrecision(field) <= 3) {
                        return convertToTimestamp(Conversions.toInstantFromMillis(x))
                    }
                    if (getTimePrecision(field) <= 6) {
                        return convertToTimestamp(Conversions.toInstantFromMicros(x))
                    }
                }
                return convertToTimestamp(x)
            }
            "DATE" -> {
                if (x == PostgresValueConverter.NEGATIVE_INFINITY_LOCAL_DATE) {
                    return NEGATIVE_INFINITY_VALUE
                }
                if (x == PostgresValueConverter.POSITIVE_INFINITY_LOCAL_DATE) {
                    return POSITIVE_INFINITY_VALUE
                }
                if (x is Int) {
                    return convertToDate(LocalDate.ofEpochDay(x.toLong()))
                }
                return convertToDate(x)
            }
            "TIME" -> return resolveTime(field, x)
            "INTERVAL" -> return convertInterval((x as org.postgresql.util.PGInterval?)!!)
            else ->
                throw IllegalArgumentException(
                    "Unknown field type  " + field.typeName().uppercase(),
                )
        }
    }

    private fun resolveTime(field: RelationalColumn, x: Any): String {
        if (x is Long) {
            if (getTimePrecision(field) <= 3) {
                val l = Math.multiplyExact(x, TimeUnit.MILLISECONDS.toNanos(1))
                return convertToTime(LocalTime.ofNanoOfDay(l))
            }
            if (getTimePrecision(field) <= 6) {
                val l = Math.multiplyExact(x, TimeUnit.MICROSECONDS.toNanos(1))
                return convertToTime(LocalTime.ofNanoOfDay(l))
            }
        }
        return convertToTime(x)
    }

    private fun convertInterval(pgInterval: PGInterval): String {
        val resultInterval = StringBuilder()
        formatDateUnit(resultInterval, pgInterval.getYears(), " year ")
        formatDateUnit(resultInterval, pgInterval.getMonths(), " mons ")
        formatDateUnit(resultInterval, pgInterval.getDays(), " days ")

        formatTimeValues(resultInterval, pgInterval)
        return resultInterval.toString()
    }

    private fun registerMoney(
        field: RelationalColumn,
        registration: CustomConverter.ConverterRegistration<SchemaBuilder?>
    ) {
        registration.register(
            SchemaBuilder.string().optional(),
            CustomConverter.Converter { x: Any? ->
                if (x == null) {
                    val defaultValue: Any? = convertDefaultValue(field)
                    return@Converter if (defaultValue == null) null
                    else
                        getMoneyConvertedValue(
                            defaultValue,
                        )
                }
                getMoneyConvertedValue(x)
            },
        )
    }

    private fun getMoneyConvertedValue(x: Any): String? {
        if (x is Double) {
            val result = BigDecimal.valueOf(x)
            if (
                result.compareTo(BigDecimal("999999999999999")) == 1 ||
                    result.compareTo(BigDecimal("-999999999999999")) == -1
            ) {
                return null
            }
            return result.toString()
        } else {
            return x.toString()
        }
    }

    private fun formatDateUnit(resultInterval: StringBuilder, dateUnit: Int, s: String?) {
        if (dateUnit != 0) {
            resultInterval.append(dateUnit).append(s)
        }
    }

    private fun formatTimeValues(resultInterval: StringBuilder, pgInterval: PGInterval) {
        if (isNegativeTime(pgInterval)) {
            resultInterval.append("-")
        }
        // TODO check if value more or less than Integer.MIN_VALUE Integer.MAX_VALUE,
        val hours = abs(pgInterval.getHours())
        val minutes = abs(pgInterval.getMinutes())
        val seconds = abs(pgInterval.getWholeSeconds())
        resultInterval.append(addFirstDigit(hours))
        resultInterval.append(hours)
        resultInterval.append(":")
        resultInterval.append(addFirstDigit(minutes))
        resultInterval.append(minutes)
        resultInterval.append(":")
        resultInterval.append(addFirstDigit(seconds))
        resultInterval.append(seconds)
    }

    private fun addFirstDigit(hours: Int): String {
        return if (hours <= 9) "0" else ""
    }

    private fun isNegativeTime(pgInterval: PGInterval): Boolean {
        return pgInterval.getHours() < 0 ||
            pgInterval.getMinutes() < 0 ||
            pgInterval.getWholeSeconds() < 0
    }

    private fun numericArrayColumnPrecisionIsNotVariable(column: RelationalColumn): Boolean {
        return column.length().orElse(VARIABLE_SCALE_DECIMAL_LENGTH) !=
            VARIABLE_SCALE_DECIMAL_LENGTH
    }

    companion object {
        private val log = KotlinLogging.logger {}

        private fun convertDefaultValue(field: RelationalColumn): Any? {
            if (field.isOptional()) {
                return null
            } else if (field.hasDefaultValue()) {
                return field.defaultValue()
            }
            return null
        }

        // adapted from Apache commons codec Hex
        private fun encodeHexString(data: ByteArray): String {
            // two characters form the hex value.
            val length = data.size
            val out = CharArray(length shl 1)
            var i = 0
            var j = 0
            while (i < length) {
                out[j++] = HEX_DIGITS[(0xF0 and data[i].toInt()) ushr 4]
                out[j++] = HEX_DIGITS[0x0F and data[i].toInt()]
                i++
            }
            return String(out)
        }

        private val HEX_DIGITS =
            charArrayOf(
                '0',
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                'a',
                'b',
                'c',
                'd',
                'e',
                'f',
            )
    }
}
