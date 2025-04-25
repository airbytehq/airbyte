/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.node.ArrayNode
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.LegacySQLTypeName
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.util.BigqueryClientFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigDecimal
import java.time.ZoneOffset
import java.util.LinkedHashMap

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
                    row.get(Meta.COLUMN_NAME_AB_LOADED_AT).let {
                        if (it.isNull) {
                            null
                        } else {
                            it.timestampInstant.toEpochMilli()
                        }
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
                            when (field.type) {
                                LegacySQLTypeName.BOOLEAN -> BooleanValue(value.booleanValue)
                                LegacySQLTypeName.BIGNUMERIC -> NumberValue(value.numericValue)
                                LegacySQLTypeName.FLOAT ->
                                    NumberValue(BigDecimal(value.doubleValue))
                                LegacySQLTypeName.NUMERIC -> NumberValue(value.numericValue)
                                LegacySQLTypeName.INTEGER -> IntegerValue(value.longValue)
                                LegacySQLTypeName.STRING -> StringValue(value.stringValue)
                                // TODO check these
                                LegacySQLTypeName.DATE -> DateValue(value.stringValue)
                                LegacySQLTypeName.DATETIME ->
                                    TimestampWithoutTimezoneValue(value.stringValue)
                                LegacySQLTypeName.TIME ->
                                    TimeWithoutTimezoneValue(value.stringValue)
                                LegacySQLTypeName.TIMESTAMP ->
                                    TimestampWithTimezoneValue(
                                        value.timestampInstant.atOffset(ZoneOffset.UTC)
                                    )
                                LegacySQLTypeName.JSON ->
                                    value.stringValue.deserializeToNode().toAirbyteValue()
                                else ->
                                    throw UnsupportedOperationException(
                                        "Bigquery data dumper doesn't know how to dump type ${field.type} with value $value"
                                    )
                            }
                        field.name to airbyteValue
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
