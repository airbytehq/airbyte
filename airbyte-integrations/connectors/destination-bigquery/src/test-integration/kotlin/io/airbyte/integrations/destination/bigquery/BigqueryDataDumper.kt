/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.node.ArrayNode
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.LegacySQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableId
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
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryFinalTableNameGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryRawTableNameGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.time.ZoneOffset

private val logger = KotlinLogging.logger {}

object BigqueryRawTableDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = BigqueryConfigurationFactory().make(spec as BigquerySpecification)
        val bigquery = BigqueryBeansFactory().getBigqueryClient(config)

        val (_, rawTableName) =
            BigqueryRawTableNameGenerator(config).getTableName(stream.descriptor)

        return bigquery.getTable(TableId.of(config.rawTableDataset, rawTableName))?.let { table ->
            val bigquerySchema = table.getDefinition<StandardTableDefinition>().schema!!
            table.list(bigquerySchema).iterateAll().map { row ->
                OutputRecord(
                    rawId = row[Meta.COLUMN_NAME_AB_RAW_ID].stringValue,
                    extractedAt =
                        row[Meta.COLUMN_NAME_AB_EXTRACTED_AT].timestampInstant.toEpochMilli(),
                    // loadedAt is nullable (e.g. if we disabled T+D, then it will always be null)
                    loadedAt =
                        row[Meta.COLUMN_NAME_AB_LOADED_AT].mapNotNull {
                            it.timestampInstant.toEpochMilli()
                        },
                    generationId = row[Meta.COLUMN_NAME_AB_GENERATION_ID].longValue,
                    data =
                        row[Meta.COLUMN_NAME_DATA].stringValue.deserializeToNode().toAirbyteValue(),
                    airbyteMeta = stringToMeta(row[Meta.COLUMN_NAME_AB_META].stringValue),
                )
            }
        }
            ?: run {
                logger.warn {
                    "Raw table does not exist: ${config.rawTableDataset}.$rawTableName. Returning empty list."
                }
                emptyList()
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
        val bigquery = BigqueryBeansFactory().getBigqueryClient(config)

        val (datasetName, finalTableName) =
            BigqueryFinalTableNameGenerator(config).getTableName(stream.descriptor)

        return bigquery.getTable(TableId.of(datasetName, finalTableName))?.let { table ->
            val bigquerySchema = table.getDefinition<StandardTableDefinition>().schema!!
            table.list(bigquerySchema).iterateAll().map { row ->
                val valuesMap: LinkedHashMap<String, AirbyteValue> =
                    bigquerySchema.fields
                        .filter { field -> !Meta.COLUMN_NAMES.contains(field.name) }
                        .associateTo(linkedMapOf()) { field ->
                            val value: FieldValue = row[field.name]
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
                    rawId = row[Meta.COLUMN_NAME_AB_RAW_ID].stringValue,
                    extractedAt =
                        row[Meta.COLUMN_NAME_AB_EXTRACTED_AT].timestampInstant.toEpochMilli(),
                    loadedAt = null,
                    generationId = row[Meta.COLUMN_NAME_AB_GENERATION_ID].longValue,
                    data = ObjectValue(valuesMap),
                    airbyteMeta = stringToMeta(row[Meta.COLUMN_NAME_AB_META].stringValue),
                )
            }
        }
            ?: run {
                logger.warn {
                    "Final table does not exist: $datasetName.$finalTableName. Returning empty list."
                }
                return emptyList()
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
