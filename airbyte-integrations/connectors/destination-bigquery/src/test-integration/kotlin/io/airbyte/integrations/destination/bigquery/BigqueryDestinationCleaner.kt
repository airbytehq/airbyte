/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.integrations.destination.bigquery.util.BigqueryClientFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

private val logger = KotlinLogging.logger {}

class BigqueryDestinationCleaner(private val configJson: JsonNode) : DestinationCleaner {
    override fun cleanup() {
        val config = BigQueryDestinationTestUtils.parseConfig(configJson)
        val bigquery = BigqueryClientFactory(config).make()

        val oldThreshold = System.currentTimeMillis() - Duration.ofDays(RETENTION_DAYS).toMillis()

        runBlocking(Dispatchers.IO) {
            logger.info { "Cleaning up old raw tables in ${config.rawTableDataset}" }

            var rawTables = bigquery.listTables(config.rawTableDataset)
            // Page.iterateAll is _really_ slow, even if the interior function is `launch`-ed.
            // Manually page through, and launch all the deletion work, so that we're always
            // fetching new pages.
            while (true) {
                launch {
                    rawTables.values.forEach { table ->
                        val tableName = table.tableId.table
                        // in raw tables, we embed the namespace into the table name.
                        // so we have to call isNamespaceOld on the table name.
                        if (
                            IntegrationTest.isNamespaceOld(
                                tableName,
                                retentionDays = RETENTION_DAYS
                            ) ||
                                (tableNamePrefixesToDelete.any { tableName.startsWith(it) } &&
                                    table.creationTime < oldThreshold)
                        ) {
                            launch {
                                logger.info { "Deleting table ${table.tableId}" }
                                try {
                                    table.delete()
                                } catch (e: BigQueryException) {
                                    // ignore exception
                                    // e.g. someone else might be running tests at the same time,
                                    // and deleted this table before we got to it
                                }
                            }
                        }
                    }
                }
                if (rawTables.hasNextPage()) {
                    rawTables = rawTables.nextPage
                } else {
                    break
                }
            }

            logger.info { "Cleaning up old datasets in ${config.projectId}" }
            var datasets = bigquery.listDatasets(config.projectId)
            while (true) {
                launch {
                    datasets.values.forEach { plainDataset ->
                        val datasetName = plainDataset.datasetId.dataset
                        // listDatasets doesn't fetch all the dataset information.
                        // we have to manually load the creationTime field.
                        val dataset =
                            plainDataset.reload(
                                BigQuery.DatasetOption.fields(BigQuery.DatasetField.CREATION_TIME)
                            )
                        if (
                            IntegrationTest.isNamespaceOld(
                                datasetName,
                                retentionDays = RETENTION_DAYS
                            ) ||
                                (datasetNamePrefixesToDelete.any { datasetName.startsWith(it) } &&
                                    dataset.creationTime < oldThreshold)
                        ) {
                            launch {
                                logger.info { "Deleting dataset ${dataset.datasetId}" }
                                try {
                                    dataset.delete(BigQuery.DatasetDeleteOption.deleteContents())
                                } catch (e: BigQueryException) {
                                    // ignore exception.
                                    // there are some test-generated datasets that our test user
                                    // doesn't have permissions on, for... some reason
                                    // or maybe someone else is running tests at the same time as
                                    // us, and we're racing to delete these datasets.
                                }
                            }
                        }
                    }
                }
                if (datasets.hasNextPage()) {
                    datasets = datasets.nextPage
                } else {
                    break
                }
            }
        }
    }

    companion object {
        // set a more aggressive retention policy.
        // bigquery is _really_ slow at listing datasets/tables.
        const val RETENTION_DAYS = 7L

        // some older tests used these table/dataset name prefixes.
        // might as well clean them up while we're here.
        private val tableNamePrefixesToDelete =
            listOf(
                "_99namespace",
                "_airbyte_tmp",
                "tdtest_",
                "typing_deduping_test",
            )
        private val datasetNamePrefixesToDelete =
            listOf(
                "99namespace",
                "airbyte_source_namespace_",
                "airbyte_tests_",
                "bq_dest_integration_test_",
                "dest_1001_namespace_",
                "diff_sourcenamespace_",
                "namespace_with_special_character",
                "raw_namespace_",
                "sourcenamespace_",
                "sql_generator_test_",
                "tdtest_",
                "test_deleteme_",
            )
    }
}
