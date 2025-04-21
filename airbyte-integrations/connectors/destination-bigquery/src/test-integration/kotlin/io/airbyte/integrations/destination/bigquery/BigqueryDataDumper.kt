/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.node.ArrayNode
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
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

object BigqueryRawTableDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = BigqueryConfigurationFactory().make(spec as BigquerySpecification)
        val bigquery = BigqueryClientFactory(config).make()
        val namespace = stream.descriptor.namespace ?: config.datasetId
        val rawTableName =
            TypingDedupingUtil.concatenateRawTableName(namespace, stream.descriptor.name)
        val result: TableResult =
            bigquery.query(
                QueryJobConfiguration.of("SELECT * FROM ${config.rawTableDataset}.$rawTableName")
            )
        return result.iterateAll().map { row: FieldValueList ->
            rowToOutputRecord(
                row,
                row.get(Meta.COLUMN_NAME_DATA).stringValue.deserializeToNode().toAirbyteValue(),
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

// TODO final table dumper

fun rowToOutputRecord(
    row: FieldValueList,
    data: AirbyteValue,
) =
    OutputRecord(
        rawId = row.get(Meta.COLUMN_NAME_AB_RAW_ID).stringValue,
        extractedAt = row.get(Meta.COLUMN_NAME_AB_EXTRACTED_AT).timestampInstant.toEpochMilli(),
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
        data = data,
        airbyteMeta = stringToMeta(row.get(Meta.COLUMN_NAME_AB_META).stringValue),
    )

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
