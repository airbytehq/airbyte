/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.operation

import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.DatasetId
import com.google.cloud.bigquery.DatasetInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.WarehouseStorageOperationTest
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.BigQueryDestination
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGeneratorIntegrationTest
import java.nio.file.Files
import java.nio.file.Path
import java.util.stream.Stream
import kotlin.test.assertEquals
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

/**
 * Extremely barebones integration test for the direct inserts storage op. We should eventually:
 * * Make something similar for the GCS storage op
 * * Genericize this and put it in the CDK
 * * Add assertions for all the columns, not just airbyte_data
 * * Actually test all the methods on StorageOperation
 */
@Execution(ExecutionMode.CONCURRENT)
class BigQueryDirectLoadingStorageOperationTest:
    WarehouseStorageOperationTest<Stream<PartialAirbyteMessage>>(
        BigQueryDirectLoadingStorageOperation(
            bq,
            15,
            BigQueryRecordFormatter(),
            BigQuerySqlGenerator(projectId, datasetLocation),
            BigQueryDestinationHandler(bq, datasetLocation),
            datasetLocation,
        )
    ) {
    @BeforeEach
    fun setup() {
        bq.create(DatasetInfo.of(streamId.rawNamespace))
    }

    @AfterEach
    fun teardown() {
        bq.delete(
            DatasetId.of(streamId.rawNamespace),
            BigQuery.DatasetDeleteOption.deleteContents()
        )
    }

    override fun toData(vararg records: PartialAirbyteMessage): Stream<PartialAirbyteMessage> {
        return Stream.of(*records)
    }

    override fun dumpRawRecords(suffix: String): List<JsonNode> {
        val result: TableResult =
            bq.query(
                QueryJobConfiguration.of(
                    "SELECT * FROM " + streamId.rawTableId(BigQuerySqlGenerator.QUOTE, suffix)
                ),
            )
        return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result)
    }

    override fun assertThrowsTableNotFound(f: () -> Unit) {
        assertEquals(404, assertThrows<BigQueryException>(f).code)
    }

    companion object {
        private val config =
            Jsons.deserialize(Files.readString(Path.of("secrets/credentials-gcs-staging.json")))
        private val bq = BigQueryDestination.getBigQuery(config)
        private val projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText()
        private val datasetLocation = config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText()
    }
}
