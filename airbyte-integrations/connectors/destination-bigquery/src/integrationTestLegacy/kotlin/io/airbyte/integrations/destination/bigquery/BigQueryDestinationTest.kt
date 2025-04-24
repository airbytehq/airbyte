/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.bigquery.*
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.createPartitionedTableIfNotExists
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getDatasetLocation
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getGcsJsonNodeConfig
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getOrCreateDataset
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.util.*
import org.junit.jupiter.api.*
import org.mockito.Mockito.mock
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
internal class BigQueryDestinationTest {
    protected var bigquery: BigQuery? = null
    protected var dataset: Dataset? = null
    private var s3Client: AmazonS3? = null

    @Throws(IOException::class)
    protected fun initBigQuery(config: JsonNode) {
        bigquery = BigQueryDestinationTestUtils.initBigQuery(config)
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

        getOrCreateDataset(bigquery!!, tmpTestSchemaName, getDatasetLocation(config))

        Assertions.assertDoesNotThrow {
            // Create table
            createPartitionedTableIfNotExists(bigquery!!, tableId, schema)

            // Try to create it one more time. Shouldn't throw exception
            createPartitionedTableIfNotExists(bigquery!!, tableId, schema)
        }
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
            Companion.config = config

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
