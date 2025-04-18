/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfigurationFactory
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.util.BigqueryClientFactory

class BigqueryRawTableDataDumper : DestinationDataDumper {
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
            OutputRecord(
                rawId = row.get(Meta.COLUMN_NAME_AB_RAW_ID).stringValue,
                extractedAt = row.get(Meta.COLUMN_NAME_AB_EXTRACTED_AT).longValue,
                loadedAt = row.get(Meta.COLUMN_NAME_AB_LOADED_AT).longValue,
                generationId = row.get(Meta.COLUMN_NAME_AB_GENERATION_ID).longValue,
                // TODO
                data = emptyMap(),
                // TODO
                airbyteMeta = null,
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
