/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

private val logger = KotlinLogging.logger {}

object BigqueryDestinationCleaner : DestinationCleaner {
    private val actualCleaner =
        BigqueryDestinationCleanerInstance(
                BigQueryDestinationTestUtils.standardInsertRawOverrideConfig
            )
            .compose(
                BigqueryDestinationCleanerInstance(
                    BigQueryDestinationTestUtils.standardInsertConfig
                )
            )

    override fun cleanup() {
        // only run the cleaner sometimes - our nightlies will do this enough of the time
        // that we have a reasonably clean destination.
        // bigquery sets pretty harsh rate limits on some of the stuff the cleaner does.
        // (would be really nice if we stuck this in a cron somewhere + trigger it weekly,
        // but this is fine for now)
        if (Math.random() < 0.1) {
            actualCleaner.cleanup()
        }
    }
}

class BigqueryDestinationCleanerInstance(private val configString: String) : DestinationCleaner {
    override fun cleanup() {
        val config = BigQueryDestinationTestUtils.parseConfig(configString)
        val bigquery = BigqueryBeansFactory().getBigqueryClient(config)

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
                            )
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
                    datasets.values.forEach { dataset ->
                        if (
                            dataset != null &&
                                IntegrationTest.isNamespaceOld(
                                    dataset.datasetId.dataset,
                                    retentionDays = RETENTION_DAYS
                                )
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
    }
}
