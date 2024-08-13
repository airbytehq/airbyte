/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.bigquery.*
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.createPartitionedTableIfNotExists
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.executeQuery
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getDatasetLocation
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getGcsJsonNodeConfig
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getOrCreateDataset
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.Stream
import java.util.stream.StreamSupport
import org.assertj.core.api.Assertions
import org.junit.jupiter.api.*
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.mockito.Mockito
import org.mockito.Mockito.mock
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
internal class BigQueryDestinationTest {
    protected var bigquery: BigQuery? = null
    protected var dataset: Dataset? = null
    private var s3Client: AmazonS3? = null

    private fun successTestConfigProviderBase(): Stream<Arguments> {
        return Stream.of(Arguments.of("config"), Arguments.of("configWithProjectId"))
    }

    private fun successTestConfigProvider(): Stream<Arguments> {
        return Stream.concat(
            successTestConfigProviderBase(),
            Stream.of(Arguments.of("gcsStagingConfig"))
        )
    }

    private fun failCheckTestConfigProvider(): Stream<Arguments> {
        return Stream.of(
            Arguments.of(
                "configWithBadProjectId",
                "User does not have bigquery.datasets.create permission in project"
            ),
            Arguments.of(
                "insufficientRoleConfig",
                "User does not have bigquery.datasets.create permission"
            ),
            Arguments.of(
                "gcsStagingConfigWithBadCopyPermission",
                "Permission bigquery.tables.updateData denied on table"
            ),
        )
    }

    private fun failWriteTestConfigProvider(): Stream<Arguments> {
        return Stream.of(
            Arguments.of(
                "configWithBadProjectId",
                "User does not have bigquery.datasets.create permission in project"
            ),
            Arguments.of(
                "noEditPublicSchemaRoleConfig",
                "Failed to write to destination schema."
            ), // (or it may not exist)
            Arguments.of("insufficientRoleConfig", "Permission bigquery.tables.create denied")
        )
    }

    @Throws(IOException::class)
    protected fun initBigQuery(config: JsonNode) {
        bigquery = BigQueryDestinationTestUtils.initBigQuery(config, projectId)
        try {
            dataset = BigQueryDestinationTestUtils.initDataSet(config, bigquery, datasetId)
        } catch (ex: Exception) {
            // ignore
        }
    }

    @BeforeEach
    @Throws(IOException::class)
    fun setup(info: TestInfo) {
        if (info.displayName == "testSpec()") {
            return
        }
        bigquery = null
        dataset = null
        val gcsDestinationConfig: GcsDestinationConfig =
            GcsDestinationConfig.getGcsDestinationConfig(getGcsJsonNodeConfig(gcsStagingConfig!!))
        this.s3Client = gcsDestinationConfig.getS3Client()
    }

    @AfterEach
    fun tearDown(info: TestInfo) {
        if (info.displayName == "testSpec()") {
            return
        }
        BigQueryDestinationTestUtils.tearDownBigQuery(bigquery, dataset, LOGGER)
        BigQueryDestinationTestUtils.tearDownGcs(s3Client, config, LOGGER)
    }

    @Test
    @Throws(Exception::class)
    fun testSpec() {
        val actual = BigQueryDestination().spec()
        val resourceString = readResource("spec.json")
        val expected = deserialize(resourceString, ConnectorSpecification::class.java)

        org.junit.jupiter.api.Assertions.assertEquals(expected, actual)
    }

    @ParameterizedTest
    @MethodSource("successTestConfigProvider")
    @Throws(IOException::class)
    fun testCheckSuccess(configName: String) {
        val testConfig = configs!![configName]
        val actual = BigQueryDestination().check(testConfig!!)
        val expected =
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        org.junit.jupiter.api.Assertions.assertEquals(expected, actual)
    }

    @ParameterizedTest
    @MethodSource("failCheckTestConfigProvider")
    fun testCheckFailures(configName: String, error: String?) {
        // TODO: this should always throw ConfigErrorException
        val testConfig = configs!![configName]

        val ex =
            org.junit.jupiter.api.Assertions.assertThrows(Exception::class.java) {
                BigQueryDestination().check(testConfig!!)
            }
        Assertions.assertThat(ex.message).contains(error)
    }

    @Disabled
    @ParameterizedTest
    @MethodSource("successTestConfigProvider")
    @Throws(Exception::class)
    fun testWriteSuccess(configName: String) {
        initBigQuery(config)
        val testConfig = configs!![configName]
        val destination = BigQueryDestination()
        val consumer =
            destination.getConsumer(testConfig!!, catalog!!) { message: AirbyteMessage? ->
                Destination.defaultOutputRecordCollector(message)
            }

        consumer!!.start()
        consumer.accept(MESSAGE_USERS1)
        consumer.accept(MESSAGE_TASKS1)
        consumer.accept(MESSAGE_USERS2)
        consumer.accept(MESSAGE_TASKS2)
        consumer.accept(MESSAGE_STATE)
        consumer.close()

        val usersActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(USERS_STREAM_NAME))
        val expectedUsersJson: List<JsonNode> =
            Lists.newArrayList(MESSAGE_USERS1.record.data, MESSAGE_USERS2.record.data)
        org.junit.jupiter.api.Assertions.assertEquals(expectedUsersJson.size, usersActual.size)
        org.junit.jupiter.api.Assertions.assertTrue(
            expectedUsersJson.containsAll(usersActual) && usersActual.containsAll(expectedUsersJson)
        )

        val tasksActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(TASKS_STREAM_NAME))
        val expectedTasksJson: List<JsonNode> =
            Lists.newArrayList(MESSAGE_TASKS1.record.data, MESSAGE_TASKS2.record.data)
        org.junit.jupiter.api.Assertions.assertEquals(expectedTasksJson.size, tasksActual.size)
        org.junit.jupiter.api.Assertions.assertTrue(
            expectedTasksJson.containsAll(tasksActual) && tasksActual.containsAll(expectedTasksJson)
        )

        assertTmpTablesNotPresent(
            catalog!!
                .streams
                .stream()
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { obj: AirbyteStream -> obj.name }
                .collect(Collectors.toList())
        )
    }

    @Test
    @Throws(Exception::class)
    fun testCreateTableSuccessWhenTableAlreadyExists() {
        initBigQuery(config)

        // Test schema where we will try to re-create existing table
        val tmpTestSchemaName = "test_create_table_when_exists_schema"

        val schema =
            Schema.of(
                com.google.cloud.bigquery.Field.of(
                    JavaBaseConstants.COLUMN_NAME_AB_ID,
                    StandardSQLTypeName.STRING
                ),
                com.google.cloud.bigquery.Field.of(
                    JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                    StandardSQLTypeName.TIMESTAMP
                ),
                com.google.cloud.bigquery.Field.of(
                    JavaBaseConstants.COLUMN_NAME_DATA,
                    StandardSQLTypeName.STRING
                )
            )

        val tableId = TableId.of(tmpTestSchemaName, "test_already_existing_table")

        getOrCreateDataset(bigquery!!, tmpTestSchemaName, getDatasetLocation(config!!))

        org.junit.jupiter.api.Assertions.assertDoesNotThrow {
            // Create table
            createPartitionedTableIfNotExists(bigquery!!, tableId, schema)

            // Try to create it one more time. Shouldn't throw exception
            createPartitionedTableIfNotExists(bigquery!!, tableId, schema)
        }
    }

    @Disabled
    @ParameterizedTest
    @MethodSource("failWriteTestConfigProvider")
    @Throws(Exception::class)
    fun testWriteFailure(configName: String, error: String?) {
        initBigQuery(config)
        val testConfig = configs!![configName]
        val ex =
            org.junit.jupiter.api.Assertions.assertThrows<Exception>(Exception::class.java) {
                val consumer =
                    Mockito.spy<AirbyteMessageConsumer?>(
                        BigQueryDestination().getConsumer(testConfig!!, catalog!!) {
                            message: AirbyteMessage? ->
                            Destination.defaultOutputRecordCollector(message)
                        }
                    )
                consumer!!.start()
            }
        Assertions.assertThat(ex.message).contains(error)

        val tableNames =
            catalog!!
                .streams
                .stream()
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { obj: AirbyteStream -> obj.name }
                .toList()
        assertTmpTablesNotPresent(
            catalog!!
                .streams
                .stream()
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { obj: AirbyteStream -> obj.name }
                .collect(Collectors.toList())
        )
        // assert that no tables were created.
        org.junit.jupiter.api.Assertions.assertTrue(
            fetchNamesOfTablesInDb().stream().noneMatch { tableName: String ->
                tableNames.stream().anyMatch { prefix: String -> tableName.startsWith(prefix) }
            }
        )
    }

    @Throws(InterruptedException::class)
    private fun fetchNamesOfTablesInDb(): Set<String> {
        if (dataset == null || bigquery == null) {
            return emptySet()
        }
        val queryConfig =
            QueryJobConfiguration.newBuilder(
                    String.format(
                        "SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES`;",
                        dataset!!.datasetId.dataset
                    )
                )
                .setUseLegacySql(false)
                .build()

        if (!dataset!!.exists()) {
            return emptySet()
        }
        return StreamSupport.stream(
                executeQuery(bigquery!!, queryConfig)
                    .getLeft()
                    .getQueryResults()
                    .iterateAll()
                    .spliterator(),
                false
            )
            .map { v: FieldValueList -> v["TABLE_NAME"].stringValue }
            .collect(Collectors.toSet())
    }

    @Throws(InterruptedException::class)
    private fun assertTmpTablesNotPresent(tableNames: List<String>) {
        val tmpTableNamePrefixes =
            tableNames.stream().map { name: String -> name + "_" }.collect(Collectors.toSet())
        val finalTableNames =
            tableNames.stream().map { name: String -> name + "_raw" }.collect(Collectors.toSet())
        // search for table names that have the tmp table prefix but are not raw tables.
        org.junit.jupiter.api.Assertions.assertTrue(
            fetchNamesOfTablesInDb()
                .stream()
                .filter { tableName: String -> !finalTableNames.contains(tableName) }
                .noneMatch { tableName: String ->
                    tmpTableNamePrefixes.stream().anyMatch { prefix: String ->
                        tableName.startsWith(prefix)
                    }
                }
        )
    }

    @Throws(Exception::class)
    private fun retrieveRecords(tableName: String): List<JsonNode> {
        val queryConfig =
            QueryJobConfiguration.newBuilder(
                    String.format(
                        "SELECT * FROM `%s.%s`;",
                        dataset!!.datasetId.dataset,
                        tableName.lowercase(Locale.getDefault())
                    )
                )
                .setUseLegacySql(false)
                .build()

        executeQuery(bigquery!!, queryConfig)

        return StreamSupport.stream<FieldValueList>(
                executeQuery(bigquery!!, queryConfig)
                    .getLeft()
                    .getQueryResults()
                    .iterateAll()
                    .spliterator(),
                false
            )
            .map<String>(
                Function<FieldValueList, String> { v: FieldValueList ->
                    v.get(JavaBaseConstants.COLUMN_NAME_DATA).getStringValue()
                }
            )
            .map<JsonNode> { jsonString: String? -> deserialize(jsonString) }
            .collect(Collectors.toList<JsonNode>())
    }

    @Disabled
    @ParameterizedTest
    @MethodSource("successTestConfigProviderBase")
    @Throws(Exception::class)
    fun testWritePartitionOverUnpartitioned(configName: String) {
        val testConfig = configs!![configName]
        initBigQuery(config)
        val streamId =
            BigQuerySqlGenerator(projectId, null)
                .buildStreamId(
                    datasetId!!,
                    USERS_STREAM_NAME,
                    JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                )
        val dataset =
            BigQueryDestinationTestUtils.initDataSet(config, bigquery, streamId.rawNamespace)
        createUnpartitionedTable(bigquery!!, dataset, streamId.rawName)
        org.junit.jupiter.api.Assertions.assertFalse(
            isTablePartitioned(bigquery!!, dataset, streamId.rawName)
        )
        val destination = BigQueryDestination()
        val consumer =
            destination.getConsumer(testConfig!!, catalog!!) { message: AirbyteMessage? ->
                Destination.defaultOutputRecordCollector(message)
            }

        consumer!!.start()
        consumer.accept(MESSAGE_USERS1)
        consumer.accept(MESSAGE_TASKS1)
        consumer.accept(MESSAGE_USERS2)
        consumer.accept(MESSAGE_TASKS2)
        consumer.accept(MESSAGE_STATE)
        consumer.close()

        val usersActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(USERS_STREAM_NAME))
        val expectedUsersJson: List<JsonNode> =
            Lists.newArrayList(MESSAGE_USERS1.record.data, MESSAGE_USERS2.record.data)
        org.junit.jupiter.api.Assertions.assertEquals(expectedUsersJson.size, usersActual.size)
        org.junit.jupiter.api.Assertions.assertTrue(
            expectedUsersJson.containsAll(usersActual) && usersActual.containsAll(expectedUsersJson)
        )

        val tasksActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(TASKS_STREAM_NAME))
        val expectedTasksJson: List<JsonNode> =
            Lists.newArrayList(MESSAGE_TASKS1.record.data, MESSAGE_TASKS2.record.data)
        org.junit.jupiter.api.Assertions.assertEquals(expectedTasksJson.size, tasksActual.size)
        org.junit.jupiter.api.Assertions.assertTrue(
            expectedTasksJson.containsAll(tasksActual) && tasksActual.containsAll(expectedTasksJson)
        )

        assertTmpTablesNotPresent(
            catalog!!
                .streams
                .stream()
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { obj: AirbyteStream -> obj.name }
                .collect(Collectors.toList())
        )
        org.junit.jupiter.api.Assertions.assertTrue(
            isTablePartitioned(bigquery!!, dataset, streamId.rawName)
        )
    }

    private fun createUnpartitionedTable(
        bigquery: BigQuery?,
        dataset: Dataset?,
        tableName: String
    ) {
        val tableId = TableId.of(dataset!!.datasetId.dataset, tableName)
        bigquery!!.delete(tableId)
        val schema =
            Schema.of(
                com.google.cloud.bigquery.Field.of(
                    JavaBaseConstants.COLUMN_NAME_AB_ID,
                    StandardSQLTypeName.STRING
                ),
                com.google.cloud.bigquery.Field.of(
                    JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
                    StandardSQLTypeName.TIMESTAMP
                ),
                com.google.cloud.bigquery.Field.of(
                    JavaBaseConstants.COLUMN_NAME_DATA,
                    StandardSQLTypeName.STRING
                )
            )
        val tableDefinition = StandardTableDefinition.newBuilder().setSchema(schema).build()
        val tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build()
        bigquery.create(tableInfo)
    }

    @Throws(InterruptedException::class)
    private fun isTablePartitioned(
        bigquery: BigQuery?,
        dataset: Dataset?,
        tableName: String
    ): Boolean {
        val queryConfig =
            QueryJobConfiguration.newBuilder(
                    String.format(
                        "SELECT max(is_partitioning_column) as is_partitioned FROM `%s.%s.INFORMATION_SCHEMA.COLUMNS` WHERE TABLE_NAME = '%s';",
                        bigquery!!.options.projectId,
                        dataset!!.datasetId.dataset,
                        tableName
                    )
                )
                .setUseLegacySql(false)
                .build()
        val result = executeQuery(bigquery, queryConfig)
        for (row in result.getLeft().getQueryResults().values) {
            return !row["is_partitioned"].isNull && row["is_partitioned"].stringValue == "YES"
        }
        return false
    }

    companion object {
        protected val CREDENTIALS_STANDARD_INSERT_PATH: Path =
            Path.of("secrets/credentials-standard.json")
        protected val CREDENTIALS_BAD_PROJECT_PATH: Path =
            Path.of("secrets/credentials-badproject.json")
        protected val CREDENTIALS_NO_DATASET_CREATION_PATH: Path =
            Path.of("secrets/credentials-standard-no-dataset-creation.json")
        protected val CREDENTIALS_NON_BILLABLE_PROJECT_PATH: Path =
            Path.of("secrets/credentials-standard-non-billable-project.json")
        protected val CREDENTIALS_NO_EDIT_PUBLIC_SCHEMA_ROLE_PATH: Path =
            Path.of("secrets/credentials-no-edit-public-schema-role.json")
        protected val CREDENTIALS_WITH_GCS_STAGING_PATH: Path =
            Path.of("secrets/credentials-gcs-staging.json")
        protected val CREDENTIALS_WITH_GCS_BAD_COPY_PERMISSION_PATH: Path =
            Path.of("secrets/credentials-1s1t-gcs-bad-copy-permission.json")

        protected val ALL_PATHS: Array<Path> =
            arrayOf(
                CREDENTIALS_STANDARD_INSERT_PATH,
                CREDENTIALS_BAD_PROJECT_PATH,
                CREDENTIALS_NO_DATASET_CREATION_PATH,
                CREDENTIALS_NO_EDIT_PUBLIC_SCHEMA_ROLE_PATH,
                CREDENTIALS_NON_BILLABLE_PROJECT_PATH,
                CREDENTIALS_WITH_GCS_STAGING_PATH,
                CREDENTIALS_WITH_GCS_BAD_COPY_PERMISSION_PATH
            )

        private val LOGGER: Logger = LoggerFactory.getLogger(BigQueryDestinationTest::class.java)
        private const val DATASET_NAME_PREFIX = "bq_dest_integration_test"

        private val NOW: Instant = Instant.now()
        protected const val USERS_STREAM_NAME: String = "users"
        protected const val TASKS_STREAM_NAME: String = "tasks"
        protected val MESSAGE_USERS1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(USERS_STREAM_NAME)
                        .withData(
                            jsonNode(
                                ImmutableMap.builder<Any, Any>()
                                    .put("name", "john")
                                    .put("id", "10")
                                    .build()
                            )
                        )
                        .withEmittedAt(NOW.toEpochMilli())
                )
        protected val MESSAGE_USERS2: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(USERS_STREAM_NAME)
                        .withData(
                            jsonNode(
                                ImmutableMap.builder<Any, Any>()
                                    .put("name", "susan")
                                    .put("id", "30")
                                    .build()
                            )
                        )
                        .withEmittedAt(NOW.toEpochMilli())
                )
        protected val MESSAGE_TASKS1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(TASKS_STREAM_NAME)
                        .withData(
                            jsonNode(
                                ImmutableMap.builder<Any, Any>()
                                    .put("goal", "announce the game.")
                                    .build()
                            )
                        )
                        .withEmittedAt(NOW.toEpochMilli())
                )
        protected val MESSAGE_TASKS2: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(TASKS_STREAM_NAME)
                        .withData(
                            jsonNode(
                                ImmutableMap.builder<Any, Any>()
                                    .put("goal", "ship some code.")
                                    .build()
                            )
                        )
                        .withEmittedAt(NOW.toEpochMilli())
                )
        protected val MESSAGE_STATE: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withData(
                            jsonNode(
                                ImmutableMap.builder<Any, Any>().put("checkpoint", "now!").build()
                            )
                        )
                )

        private val NAMING_RESOLVER: NamingConventionTransformer = BigQuerySQLNameTransformer()

        protected var projectId: String? = null
        protected var datasetId: String? = null
        protected var config: JsonNode = mock()
        protected var configWithProjectId: JsonNode? = null
        protected var configWithBadProjectId: JsonNode? = null
        protected var insufficientRoleConfig: JsonNode? = null
        protected var noEditPublicSchemaRoleConfig: JsonNode? = null
        protected var nonBillableConfig: JsonNode? = null
        protected var gcsStagingConfig: JsonNode? =
            null // default BigQuery config. Also used for setup/teardown
        protected var gcsStagingConfigWithBadCopyPermission: JsonNode? = null

        protected var configs: Map<String, JsonNode>? = null
        protected var catalog: ConfiguredAirbyteCatalog? = null

        @BeforeAll
        @Throws(IOException::class)
        @JvmStatic
        fun beforeAll() {
            for (path in ALL_PATHS) {
                check(Files.exists(path)) {
                    String.format(
                        "Must provide path to a big query credentials file. Please add file with credentials to %s",
                        path.toAbsolutePath()
                    )
                }
            }

            datasetId = addRandomSuffix(DATASET_NAME_PREFIX, "_", 8)
            val stagingPath = addRandomSuffix("test_path", "_", 8)
            // Set up config objects for test scenarios
            // config - basic config for standard inserts that should succeed check and write tests
            // this config is also used for housekeeping (checking records, and cleaning up)
            val config: JsonNode =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_STANDARD_INSERT_PATH,
                    datasetId,
                    stagingPath
                )

            DestinationConfig.initialize(config)

            // all successful configs use the same project ID
            projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText()
            this.config = config

            // configWithProjectId - config that uses project:dataset notation for rawNamespace
            val dataSetWithProjectId = String.format("%s:%s", projectId, datasetId)
            configWithProjectId =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_STANDARD_INSERT_PATH,
                    dataSetWithProjectId,
                    stagingPath
                )

            // configWithBadProjectId - config that uses "fake" project ID and should fail
            val dataSetWithBadProjectId = String.format("%s:%s", "fake", datasetId)
            configWithBadProjectId =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_BAD_PROJECT_PATH,
                    dataSetWithBadProjectId,
                    stagingPath
                )

            // config that has insufficient privileges
            insufficientRoleConfig =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_NO_DATASET_CREATION_PATH,
                    datasetId,
                    stagingPath
                )
            // config that tries to write to a project with disabled billing (free tier)
            nonBillableConfig =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_NON_BILLABLE_PROJECT_PATH,
                    "testnobilling",
                    stagingPath
                )
            // config that has no privileges to edit anything in Public schema
            noEditPublicSchemaRoleConfig =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_NO_EDIT_PUBLIC_SCHEMA_ROLE_PATH,
                    "public",
                    stagingPath
                )
            // config with GCS staging
            gcsStagingConfig =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_WITH_GCS_STAGING_PATH,
                    datasetId,
                    stagingPath
                )

            gcsStagingConfigWithBadCopyPermission =
                BigQueryDestinationTestUtils.createConfig(
                    CREDENTIALS_WITH_GCS_BAD_COPY_PERMISSION_PATH,
                    datasetId,
                    stagingPath
                )

            MESSAGE_USERS1.record.namespace = datasetId
            MESSAGE_USERS2.record.namespace = datasetId
            MESSAGE_TASKS1.record.namespace = datasetId
            MESSAGE_TASKS2.record.namespace = datasetId

            catalog =
                ConfiguredAirbyteCatalog()
                    .withStreams(
                        Lists.newArrayList(
                            CatalogHelpers.createConfiguredAirbyteStream(
                                    USERS_STREAM_NAME,
                                    datasetId,
                                    Field.of("name", JsonSchemaType.STRING),
                                    Field.of("id", JsonSchemaType.STRING)
                                )
                                .withDestinationSyncMode(DestinationSyncMode.APPEND),
                            CatalogHelpers.createConfiguredAirbyteStream(
                                TASKS_STREAM_NAME,
                                datasetId,
                                Field.of("goal", JsonSchemaType.STRING)
                            )
                        )
                    )

            configs =
                mapOf(
                    "config" to config,
                    "configWithProjectId" to configWithProjectId!!,
                    "configWithBadProjectId" to configWithBadProjectId!!,
                    "insufficientRoleConfig" to insufficientRoleConfig!!,
                    "noEditPublicSchemaRoleConfig" to noEditPublicSchemaRoleConfig!!,
                    "nonBillableConfig" to nonBillableConfig!!,
                    "gcsStagingConfig" to gcsStagingConfig!!,
                    "gcsStagingConfigWithBadCopyPermission" to
                        gcsStagingConfigWithBadCopyPermission!!,
                )
        }
    }
}
