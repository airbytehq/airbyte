/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.*
import com.google.common.collect.Streams
import io.airbyte.cdk.db.bigquery.BigQueryResultSet
import io.airbyte.cdk.db.bigquery.BigQuerySourceOperations
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces.isOlderThan2Days
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.executeQuery
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getDatasetId
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import java.io.IOException
import java.nio.file.Path
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@Disabled
abstract class AbstractBigQueryDestinationAcceptanceTest : DestinationAcceptanceTest() {
    protected var secretsFile: Path? = null
    protected var bigquery: BigQuery? = null
    protected var dataset: Dataset? = null

    protected var _config: JsonNode? = null
    protected val namingResolver: StandardNameTransformer = StandardNameTransformer()

    override val imageName: String
        get() = "airbyte/destination-bigquery:dev"

    override fun getConfig(): JsonNode {
        return _config!!
    }

    override fun getFailCheckConfig(): JsonNode? {
        (_config as ObjectNode?)!!.put(CONFIG_PROJECT_ID, "fake")
        return _config
    }

    override fun implementsNamespaces(): Boolean {
        return true
    }

    override fun supportNamespaceTest(): Boolean {
        return true
    }

    override fun getTestDataComparator(): TestDataComparator {
        return BigQueryTestDataComparator()
    }

    override fun supportBasicDataTypeTest(): Boolean {
        return true
    }

    override fun supportArrayDataTypeTest(): Boolean {
        return true
    }

    override fun supportObjectDataTypeTest(): Boolean {
        return true
    }

    override fun supportIncrementalSchemaChanges(): Boolean {
        return true
    }

    override fun getNameTransformer(): Optional<NamingConventionTransformer> {
        return Optional.of(NAME_TRANSFORMER)
    }

    override fun assertNamespaceNormalization(
        testCaseId: String?,
        expectedNormalizedNamespace: String?,
        actualNormalizedNamespace: String?
    ) {
        val message =
            String.format(
                "Test case %s failed; if this is expected, please override assertNamespaceNormalization",
                testCaseId
            )
        if (testCaseId == "S3A-1") {
            /*
             * See NamespaceTestCaseProvider for how this suffix is generated. <p> expectedNormalizedNamespace
             * will look something like this: `_99namespace_test_20230824_bicrt`. We want to grab the part after
             * `_99namespace`.
             */
            val underscoreIndex = expectedNormalizedNamespace!!.indexOf("_", 1)
            val randomSuffix = expectedNormalizedNamespace.substring(underscoreIndex)
            /*
             * bigquery allows originalNamespace starting with a number, and prepending underscore will hide the
             * dataset, so we don't do it as we do for other destinations
             */
            Assertions.assertEquals("99namespace$randomSuffix", actualNormalizedNamespace, message)
        } else {
            Assertions.assertEquals(expectedNormalizedNamespace, actualNormalizedNamespace, message)
        }
    }

    override fun getDefaultSchema(config: JsonNode): String? {
        return getDatasetId(config)
    }

    @Throws(Exception::class)
    override fun retrieveRecords(
        env: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        val streamId =
            BigQuerySqlGenerator(null, null)
                .buildStreamId(
                    namespace,
                    streamName,
                    JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                )
        return retrieveRecordsFromTable(streamId.rawName, streamId.rawNamespace)
            .stream()
            .map<String>(
                Function<JsonNode, String> { node: JsonNode ->
                    node.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()
                }
            )
            .map<JsonNode> { jsonString: String? -> deserialize(jsonString) }
            .collect(Collectors.toList<JsonNode>())
    }

    @Throws(InterruptedException::class)
    protected fun retrieveRecordsFromTable(tableName: String?, schema: String?): List<JsonNode> {
        TimeZone.setDefault(TimeZone.getTimeZone("UTC"))

        val queryConfig =
            QueryJobConfiguration.newBuilder(
                    String.format(
                        "SELECT * FROM `%s`.`%s` order by %s asc;",
                        schema,
                        tableName,
                        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
                    )
                )
                .setUseLegacySql(false)
                .setConnectionProperties(
                    listOf<ConnectionProperty>(ConnectionProperty.of("time_zone", "UTC"))
                )
                .build()

        val queryResults = executeQuery(bigquery!!, queryConfig).getLeft().getQueryResults()
        val fields = queryResults.schema!!.fields
        val sourceOperations = BigQuerySourceOperations()

        return Streams.stream(queryResults.iterateAll())
            .map { fieldValues: FieldValueList ->
                sourceOperations.rowToJson(BigQueryResultSet(fieldValues, fields))
            }
            .collect(Collectors.toList())
    }

    @Throws(IOException::class)
    protected fun setUpBigQuery() {
        // secrets file should be set by the inhereting class
        Assertions.assertNotNull(secretsFile)
        val datasetId = addRandomSuffix("airbyte_tests", "_", 8)
        val stagingPathSuffix = addRandomSuffix("test_path", "_", 8)
        val config =
            BigQueryDestinationTestUtils.createConfig(secretsFile, datasetId, stagingPathSuffix)

        val projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText()
        this._config = config
        bigquery = BigQueryDestinationTestUtils.initBigQuery(config, projectId)
        dataset = BigQueryDestinationTestUtils.initDataSet(config, bigquery, datasetId)
    }

    protected fun removeOldNamespaces() {
        var datasetsDeletedCount = 0
        // todo (cgardens) - hardcoding to testing project to de-risk this running somewhere
        // unexpected.
        for (dataset1 in
            bigquery!!
                .listDatasets("dataline-integration-testing", BigQuery.DatasetListOption.all())
                .iterateAll()) {
            if (isOlderThan2Days(dataset1.datasetId.dataset)) {
                try {
                    bigquery!!.delete(
                        dataset1.datasetId,
                        BigQuery.DatasetDeleteOption.deleteContents()
                    )
                    datasetsDeletedCount++
                } catch (e: BigQueryException) {
                    LOGGER.error("Failed to delete old dataset: {}", dataset1.datasetId.dataset, e)
                }
            }
        }
        LOGGER.info("Deleted {} old datasets.", datasetsDeletedCount)
    }

    protected fun tearDownBigQuery() {
        BigQueryDestinationTestUtils.tearDownBigQuery(bigquery, dataset, LOGGER)
    }

    companion object {
        private val NAME_TRANSFORMER: NamingConventionTransformer = BigQuerySQLNameTransformer()
        private val LOGGER: Logger =
            LoggerFactory.getLogger(AbstractBigQueryDestinationAcceptanceTest::class.java)

        protected const val CONFIG_PROJECT_ID: String = "project_id"
    }
}
