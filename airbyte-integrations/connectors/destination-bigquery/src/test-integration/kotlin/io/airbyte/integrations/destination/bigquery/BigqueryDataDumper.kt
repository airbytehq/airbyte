/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.node.ArrayNode
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.LegacySQLTypeName
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.util.BigqueryClientFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.time.ZoneOffset
import java.util.LinkedHashMap

private val logger = KotlinLogging.logger {}

object BigqueryRawTableDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = BigqueryConfigurationFactory().make(spec as BigquerySpecification)
        val bigquery = BigqueryClientFactory(config).make()

        // TODO handle special characters
        val namespace = stream.descriptor.namespace ?: config.datasetId
        val rawTableName =
            TypingDedupingUtil.concatenateRawTableName(namespace, stream.descriptor.name)

        if (bigquery.getTable(TableId.of(config.rawTableDataset, rawTableName)) == null) {
            logger.warn {
                "Raw table does not exist: $namespace.$rawTableName. Returning empty list."
            }
            return emptyList()
        }

        val result: TableResult =
            bigquery.query(
                QueryJobConfiguration.of("SELECT * FROM ${config.rawTableDataset}.$rawTableName")
            )
        return result.iterateAll().map { row: FieldValueList ->
            OutputRecord(
                rawId = row.get(Meta.COLUMN_NAME_AB_RAW_ID).stringValue,
                extractedAt =
                    row.get(Meta.COLUMN_NAME_AB_EXTRACTED_AT).timestampInstant.toEpochMilli(),
                // loadedAt is nullable (e.g. if we disabled T+D, then it will always be null)
                loadedAt =
                    row.get(Meta.COLUMN_NAME_AB_LOADED_AT).mapNotNull {
                        it.timestampInstant.toEpochMilli()
                    },
                generationId = row.get(Meta.COLUMN_NAME_AB_GENERATION_ID).longValue,
                data =
                    row.get(Meta.COLUMN_NAME_DATA).stringValue.deserializeToNode().toAirbyteValue(),
                airbyteMeta = stringToMeta(row.get(Meta.COLUMN_NAME_AB_META).stringValue),
            )
        }
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw NotImplementedError("Bigquery doesn't support file transfer")
    }
}

object BigqueryFinalTableDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = BigqueryConfigurationFactory().make(spec as BigquerySpecification)
        val bigquery = BigqueryClientFactory(config).make()

        // TODO handle special characters
        val namespace = stream.descriptor.namespace ?: config.datasetId
        val name = stream.descriptor.name

        if (bigquery.getTable(TableId.of(namespace, name)) == null) {
            logger.warn { "Final table does not exist: $namespace.$name. Returning empty list." }
            return emptyList()
        }

        val result: TableResult =
            bigquery.query(QueryJobConfiguration.of("SELECT * FROM $namespace.$name"))
        return result.iterateAll().map { row: FieldValueList ->
            val valuesMap: LinkedHashMap<String, AirbyteValue> =
                result.schema!!
                    .fields
                    .filter { field -> !Meta.COLUMN_NAMES.contains(field.name) }
                    .associateTo(linkedMapOf()) { field ->
                        val value: FieldValue = row.get(field.name)
                        val airbyteValue =
                            value.mapNotNull {
                                when (field.type) {
                                    LegacySQLTypeName.BOOLEAN -> BooleanValue(it.booleanValue)
                                    LegacySQLTypeName.BIGNUMERIC -> NumberValue(it.numericValue)
                                    LegacySQLTypeName.FLOAT ->
                                        NumberValue(BigDecimal(it.doubleValue))
                                    LegacySQLTypeName.NUMERIC -> NumberValue(it.numericValue)
                                    LegacySQLTypeName.INTEGER -> IntegerValue(it.longValue)
                                    LegacySQLTypeName.STRING -> StringValue(it.stringValue)
                                    // TODO check these
                                    LegacySQLTypeName.DATE -> DateValue(it.stringValue)
                                    LegacySQLTypeName.DATETIME ->
                                        TimestampWithoutTimezoneValue(it.stringValue)
                                    LegacySQLTypeName.TIME ->
                                        TimeWithoutTimezoneValue(it.stringValue)
                                    LegacySQLTypeName.TIMESTAMP ->
                                        TimestampWithTimezoneValue(
                                            it.timestampInstant.atOffset(ZoneOffset.UTC)
                                        )
                                    LegacySQLTypeName.JSON ->
                                        it.stringValue.deserializeToNode().toAirbyteValue()
                                    else ->
                                        throw UnsupportedOperationException(
                                            "Bigquery data dumper doesn't know how to dump type ${field.type} with value $it"
                                        )
                                }
                            }
                        field.name to (airbyteValue ?: NullValue)
                    }
            OutputRecord(
                rawId = row.get(Meta.COLUMN_NAME_AB_RAW_ID).stringValue,
                extractedAt =
                    row.get(Meta.COLUMN_NAME_AB_EXTRACTED_AT).timestampInstant.toEpochMilli(),
                loadedAt = null,
                generationId = row.get(Meta.COLUMN_NAME_AB_GENERATION_ID).longValue,
                data = ObjectValue(valuesMap),
                airbyteMeta = stringToMeta(row.get(Meta.COLUMN_NAME_AB_META).stringValue),
            )
        }
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw NotImplementedError("Bigquery doesn't support file transfer")
    }
}

fun stringToMeta(metaAsString: String): OutputRecord.Meta {
    val metaJson = Jsons.readTree(metaAsString)

    val changes =
        (metaJson["changes"] as ArrayNode).map { change ->
            Meta.Change(
                field = change["field"].textValue(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(change["change"].textValue()),
                reason = Reason.fromValue(change["reason"].textValue()),
            )
        }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"].longValue(),
    )
}

fun <T> FieldValue.mapNotNull(f: (FieldValue) -> T): T? {
    return if (this.isNull) {
        null
    } else {
        f(this)
    }
}
