/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.formatter

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.QueryParameterValue
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.util.concurrent.TimeUnit

/**
 * The class formats incoming JsonSchema and AirbyteRecord in order to be inline with a
 * corresponding uploader.
 */
class BigQueryRecordFormatter {

    fun formatRecord(record: DestinationRecordRaw): String {
        val enrichedRecord = record.asEnrichedDestinationRecordAirbyteValue()

        val outputRecord = mutableMapOf<String, Any?>()
        enrichedRecord.airbyteMetaFields.forEach { (key, value) ->
            when (key) {
                Meta.COLUMN_NAME_AB_EXTRACTED_AT -> {
                    val extractedAtMillis = (value.abValue as IntegerValue).value.longValueExact()
                    outputRecord[key] = getExtractedAt(extractedAtMillis)
                }
                Meta.COLUMN_NAME_AB_META -> {
                    // TODO this is a hack for T+D, we should remove it for direct-load tables
                    //   we're completely ignoring the enrichedRecord's meta value, because that
                    //   includes changes in-connector type coercion
                    //   and for raw tables, we only want changes that originated from the source
                    if (record.rawData.record.meta == null) {
                        record.rawData.record.meta = AirbyteRecordMessageMeta()
                        record.rawData.record.meta.changes = emptyList()
                    }
                    record.rawData.record.meta.additionalProperties["sync_id"] =
                        record.stream.syncId
                    outputRecord[key] = record.rawData.record.meta.serializeToString()
                    // TODO we should do this for direct-load tables
                    // val serializedAirbyteMeta = (value.abValue as
                    // ObjectValue).serializeToString()
                    // outputRecord[key] = serializedAirbyteMeta
                }
                Meta.COLUMN_NAME_AB_RAW_ID ->
                    outputRecord[key] = (value.abValue as StringValue).value
                Meta.COLUMN_NAME_AB_GENERATION_ID ->
                    outputRecord[key] = (value.abValue as IntegerValue).value
            }
        }

        outputRecord[Meta.COLUMN_NAME_DATA] = record.asRawJson().serializeToString()

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
    }
}
