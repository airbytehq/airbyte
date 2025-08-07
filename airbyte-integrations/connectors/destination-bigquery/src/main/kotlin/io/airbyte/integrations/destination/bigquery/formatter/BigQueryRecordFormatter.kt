/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.formatter

import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.QueryParameterValue
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.util.BigDecimalUtil
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigInteger
import java.math.RoundingMode
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.util.concurrent.TimeUnit

/**
 * The class formats incoming JsonSchema and AirbyteRecord in order to be inline with a
 * corresponding uploader.
 */
class BigQueryRecordFormatter(
    private val columnNameMapping: ColumnNameMapping,
    private val legacyRawTablesOnly: Boolean,
) {

    fun formatRecord(record: DestinationRecordRaw): String {
        val enrichedRecord =
            record.asEnrichedDestinationRecordAirbyteValue(respectLegacyUnions = true)

        val outputRecord = mutableMapOf<String, Any?>()
        val enrichedFieldsToIterate =
            if (legacyRawTablesOnly) {
                // in legacy raw tables mode, we only need to look at the airbyte fields.
                // and we just dump the actual data fields into the output record
                // as a JSON blob.
                outputRecord[Meta.COLUMN_NAME_DATA] = record.asJsonRecord().serializeToString()
                enrichedRecord.airbyteMetaFields
            } else {
                // but in direct-load mode, we do actually need to look at all the fields.
                enrichedRecord.allTypedFields
            }
        enrichedFieldsToIterate.forEach { (key, value) ->
            when (key) {
                Meta.COLUMN_NAME_AB_EXTRACTED_AT -> {
                    val extractedAtMillis = (value.abValue as IntegerValue).value.longValueExact()
                    outputRecord[key] = getExtractedAt(extractedAtMillis)
                }
                Meta.COLUMN_NAME_AB_META -> {
                    // do nothing for now - we'll be updating the meta field when we process
                    // other fields in this record.
                    // so we need to defer it until _after_ we process the entire record.
                }
                Meta.COLUMN_NAME_AB_RAW_ID ->
                    outputRecord[key] = (value.abValue as StringValue).value
                Meta.COLUMN_NAME_AB_GENERATION_ID ->
                    outputRecord[key] = (value.abValue as IntegerValue).value
                else -> {
                    if (!legacyRawTablesOnly) {
                        // if we're null, then just don't write a value into the output JSON,
                        // so that bigquery will load a NULL value.
                        // Otherwise, do all the type validation stuff, then write a value into
                        // the output JSON.
                        if (value.abValue != NullValue) {
                            // first, validate the value.
                            validateAirbyteValue(value)
                            // then, populate the record.
                            // Bigquery has some strict requirements for datetime / time formatting,
                            // so handle that here.
                            when (value.type) {
                                TimestampTypeWithTimezone ->
                                    outputRecord[columnNameMapping[key]!!] =
                                        formatTimestampWithTimezone(value)
                                TimestampTypeWithoutTimezone ->
                                    outputRecord[columnNameMapping[key]!!] =
                                        formatTimestampWithoutTimezone(value)
                                TimeTypeWithoutTimezone ->
                                    outputRecord[columnNameMapping[key]!!] =
                                        formatTimeWithoutTimezone(value)
                                TimeTypeWithTimezone ->
                                    outputRecord[columnNameMapping[key]!!] =
                                        formatTimeWithTimezone(value)
                                else -> outputRecord[columnNameMapping[key]!!] = value.abValue
                            }
                        }
                    }
                }
            }
        }

        // Now that we've gone through the whole record, we can process the airbyte_meta field.
        outputRecord[Meta.COLUMN_NAME_AB_META] =
            if (legacyRawTablesOnly) {
                // this is a hack - in legacy mode, we don't do any in-connector validation
                // so we just need to pass through the original record's airbyte_meta.
                // so we completely ignore `value.abValue` here.
                // (this is also probably hilariously slow, and it would be more efficient to just
                // construct the string ourselves. but legacy raw tables isn't a mode we want to put
                // a ton of effort into anyway)
                val metaNode = Jsons.valueToTree(record.rawData.sourceMeta) as ObjectNode
                metaNode.put("sync_id", record.stream.syncId)
                metaNode.serializeToString()
            } else {
                (enrichedRecord.airbyteMeta.abValue as ObjectValue).values
            }

        return outputRecord.serializeToString()
    }

    private fun getExtractedAt(extractedAtMillis: Long): String? {
        // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds
        // then use BQ helpers to string-format correctly.
        val emittedAtMicroseconds =
            TimeUnit.MICROSECONDS.convert(extractedAtMillis, TimeUnit.MILLISECONDS)
        return QueryParameterValue.timestamp(emittedAtMicroseconds).value
    }

    companion object {
        // see https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types
        private val INT64_MIN_VALUE: BigInteger = BigInteger.valueOf(Long.MIN_VALUE)
        private val INT64_MAX_VALUE: BigInteger = BigInteger.valueOf(Long.MAX_VALUE)
        private const val NUMERIC_MAX_PRECISION = 38
        private const val NUMERIC_MAX_SCALE = 9
        private val NUMERIC_MAX_VALUE =
            BigDecimalUtil()
                .maxForRange(precision = NUMERIC_MAX_PRECISION, scale = NUMERIC_MAX_SCALE)
        private val NUMERIC_MIN_VALUE = NUMERIC_MAX_VALUE.negate()
        private val DATE_MIN_VALUE = LocalDate.parse("0001-01-01")
        private val DATE_MAX_VALUE = LocalDate.parse("9999-12-31")
        private val TIMESTAMP_MIN_VALUE = OffsetDateTime.parse("0001-01-01T00:00:00Z")
        private val TIMESTAMP_MAX_VALUE = OffsetDateTime.parse("9999-12-31T23:59:59.999999Z")
        private val DATETIME_MIN_VALUE = LocalDateTime.parse("0001-01-01T00:00:00")
        private val DATETIME_MAX_VALUE = LocalDateTime.parse("9999-12-31T23:59:59.999999")

        private val DATETIME_WITH_TIMEZONE_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ISO_OFFSET_DATE_TIME
        private val DATETIME_WITHOUT_TIMEZONE_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ISO_DATE_TIME
        private val TIME_WITHOUT_TIMEZONE_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ISO_LOCAL_TIME
        private val TIME_WITH_TIMEZONE_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ISO_OFFSET_TIME

        // This is the schema used to represent the final raw table
        val SCHEMA_V2: Schema =
            Schema.of(
                Field.of(Meta.COLUMN_NAME_AB_RAW_ID, StandardSQLTypeName.STRING),
                Field.of(Meta.COLUMN_NAME_AB_EXTRACTED_AT, StandardSQLTypeName.TIMESTAMP),
                Field.of(Meta.COLUMN_NAME_AB_LOADED_AT, StandardSQLTypeName.TIMESTAMP),
                Field.of(Meta.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
                Field.of(Meta.COLUMN_NAME_AB_META, StandardSQLTypeName.STRING),
                Field.of(Meta.COLUMN_NAME_AB_GENERATION_ID, StandardSQLTypeName.INT64)
            )

        // This schema defines the CSV format used for the load job. It differs from SCHEMA_V2 by
        // omitting the COLUMN_NAME_AB_LOADED_AT field and by rearranging the column order.
        val CSV_SCHEMA: Schema =
            Schema.of(
                Field.of(Meta.COLUMN_NAME_AB_RAW_ID, StandardSQLTypeName.STRING),
                Field.of(Meta.COLUMN_NAME_AB_EXTRACTED_AT, StandardSQLTypeName.TIMESTAMP),
                Field.of(Meta.COLUMN_NAME_AB_META, StandardSQLTypeName.STRING),
                Field.of(Meta.COLUMN_NAME_AB_GENERATION_ID, StandardSQLTypeName.INT64),
                Field.of(Meta.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
            )

        private val DIRECT_LOAD_SCHEMA =
            listOf(
                Field.newBuilder(Meta.COLUMN_NAME_AB_RAW_ID, StandardSQLTypeName.STRING)
                    .setMode(Field.Mode.REQUIRED)
                    .build(),
                Field.newBuilder(Meta.COLUMN_NAME_AB_EXTRACTED_AT, StandardSQLTypeName.TIMESTAMP)
                    .setMode(Field.Mode.REQUIRED)
                    .build(),
                Field.newBuilder(Meta.COLUMN_NAME_AB_META, StandardSQLTypeName.JSON)
                    .setMode(Field.Mode.REQUIRED)
                    .build(),
                Field.newBuilder(Meta.COLUMN_NAME_AB_GENERATION_ID, StandardSQLTypeName.INT64)
                    .setMode(Field.Mode.NULLABLE)
                    .build(),
            )
        fun getDirectLoadSchema(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping,
        ): Schema {
            val userDefinedFields: List<Field> =
                stream.schema
                    .asColumns()
                    .mapKeys { (originalName, _) -> columnNameMapping[originalName]!! }
                    .mapValues { (_, type) ->
                        BigqueryDirectLoadSqlGenerator.toDialectType(type.type)
                    }
                    .map { (name, type) -> Field.of(name, type) }
            return Schema.of(DIRECT_LOAD_SCHEMA + userDefinedFields)
        }

        fun formatTimestampWithTimezone(value: EnrichedAirbyteValue): String {
            return DATETIME_WITH_TIMEZONE_FORMATTER.format(
                (value.abValue as TimestampWithTimezoneValue).value
            )
        }

        fun formatTimestampWithoutTimezone(value: EnrichedAirbyteValue): String {
            return DATETIME_WITHOUT_TIMEZONE_FORMATTER.format(
                (value.abValue as TimestampWithoutTimezoneValue).value
            )
        }

        fun formatTimeWithoutTimezone(value: EnrichedAirbyteValue): String {
            return TIME_WITHOUT_TIMEZONE_FORMATTER.format(
                (value.abValue as TimeWithoutTimezoneValue).value
            )
        }

        fun formatTimeWithTimezone(value: EnrichedAirbyteValue): String {
            return TIME_WITH_TIMEZONE_FORMATTER.format(
                (value.abValue as TimeWithTimezoneValue).value
            )
        }

        fun validateAirbyteValue(value: EnrichedAirbyteValue) {
            when (value.type) {
                is IntegerType -> {
                    (value.abValue as IntegerValue).value.let {
                        if (it < INT64_MIN_VALUE || INT64_MAX_VALUE < it) {
                            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                        }
                    }
                }
                is NumberType -> {
                    (value.abValue as NumberValue).value.let {
                        if (it < NUMERIC_MIN_VALUE || NUMERIC_MAX_VALUE < it) {
                            // If we're too large/small, then we have to null out.
                            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                        } else if (it.scale() > NUMERIC_MAX_SCALE) {
                            // But if we're within the min/max range, but have too many decimal
                            // points, then we can round off the number.
                            // experimentally, bigquery uses the half_up rounding strategy:
                            // select cast(json_query('{"foo": -0.0000000005}', "$.foo") as numeric)
                            // -> -0.000000001
                            // select cast(json_query('{"foo":  0.0000000005}', "$.foo") as numeric)
                            // ->  0.000000001
                            value.truncate(
                                NumberValue(it.setScale(NUMERIC_MAX_SCALE, RoundingMode.HALF_UP)),
                                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                            )
                        }
                    }
                }
                // NOTE: This validation is currently unreachable because our coercion logic in
                // AirbyteValueCoercer already rejects date/time values outside supported ranges
                // via DATE_TIME_FORMATTER and TIME_FORMATTER, the Meta change reason will therefore
                // always be DESTINATION_SERIALIZATION_ERROR instead of
                // DESTINATION_FIELD_SIZE_LIMITATION for now.
                //
                // However, we're planning to expand the supported date/time range in the coercion
                // layer, which will make this validation relevant again. Keeping this code for
                // that future change.
                is DateType -> {
                    (value.abValue as DateValue).value.let {
                        if (it < DATE_MIN_VALUE || DATE_MAX_VALUE < it) {
                            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                        }
                    }
                }
                is TimestampTypeWithTimezone -> {
                    (value.abValue as TimestampWithTimezoneValue).value.let {
                        if (it < TIMESTAMP_MIN_VALUE || TIMESTAMP_MAX_VALUE < it) {
                            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                        }
                    }
                }
                is TimestampTypeWithoutTimezone -> {
                    (value.abValue as TimestampWithoutTimezoneValue).value.let {
                        if (it < DATETIME_MIN_VALUE || DATETIME_MAX_VALUE < it) {
                            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
                        }
                    }
                }
                else -> {}
            }
        }
    }
}
