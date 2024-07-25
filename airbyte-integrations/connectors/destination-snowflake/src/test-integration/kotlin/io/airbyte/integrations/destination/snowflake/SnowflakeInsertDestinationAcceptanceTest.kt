/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import java.nio.file.Path
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*
import java.util.stream.Collectors
import javax.sql.DataSource
import org.assertj.core.api.AssertionsForClassTypes
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource

@Disabled
open class SnowflakeInsertDestinationAcceptanceTest : DestinationAcceptanceTest() {
    // this config is based on the static config, and it contains a random
    // schema name that is different for each test run
    open val staticConfig: JsonNode
        get() {
            val insertConfig = deserialize(readFile(Path.of("secrets/insert_config.json")))
            return insertConfig
        }
    private var config: JsonNode = Jsons.clone(staticConfig)
    private var dataSource: DataSource =
        SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
    private var database: JdbcDatabase = SnowflakeDatabaseUtils.getDatabase(dataSource)

    @BeforeEach
    fun setup() {
        DestinationConfig.initialize(getConfig())
    }

    override val imageName: String
        get() = "airbyte/destination-snowflake:dev"

    override fun getConfig(): JsonNode {
        return config
    }

    override fun getTestDataComparator(): TestDataComparator {
        return SnowflakeTestDataComparator()
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

    override fun supportsInDestinationNormalization(): Boolean {
        return true
    }

    override fun getFailCheckConfig(): JsonNode? {
        val invalidConfig: JsonNode = Jsons.clone<JsonNode>(config)
        (invalidConfig["credentials"] as ObjectNode).put("password", "wrong password")
        return invalidConfig
    }

    @Throws(Exception::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        val streamId =
            SnowflakeSqlGenerator(0)
                .buildStreamId(
                    namespace,
                    streamName,
                    JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                )
        return retrieveRecordsFromTable(streamId.rawName, streamId.rawNamespace)
            .stream()
            .map { r: JsonNode -> r.get(JavaBaseConstants.COLUMN_NAME_DATA) }
            .collect(Collectors.toList<JsonNode>())
    }

    override fun implementsNamespaces(): Boolean {
        return true
    }

    override fun supportNamespaceTest(): Boolean {
        return true
    }

    override fun getNameTransformer(): Optional<NamingConventionTransformer> {
        return Optional.of(NAME_TRANSFORMER)
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    @Throws(Exception::class)
    override fun retrieveNormalizedRecords(
        testEnv: TestDestinationEnv?,
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        val tableName = NAME_TRANSFORMER.getIdentifier(streamName!!)
        val schema = NAME_TRANSFORMER.getNamespace(namespace!!)
        return retrieveRecordsFromTable(tableName, schema)
    }

    @Throws(SQLException::class)
    private fun retrieveRecordsFromTable(tableName: String, schema: String): List<JsonNode> {
        val timeZone = TimeZone.getTimeZone("UTC")
        TimeZone.setDefault(timeZone)

        return database.bufferedResultSetQuery<JsonNode>(
            { connection: Connection ->
                connection
                    .createStatement()
                    .executeQuery(
                        String.format("SHOW TABLES LIKE '%s' IN SCHEMA \"%s\";", tableName, schema)
                    )
                    .use { tableInfo ->
                        Assertions.assertTrue(tableInfo.next())
                        // check that we're creating permanent tables. DBT defaults to transient
                        // tables, which have
                        // `TRANSIENT` as the value for the `kind` column.
                        Assertions.assertEquals("TABLE", tableInfo.getString("kind"))
                        connection.createStatement().execute("ALTER SESSION SET TIMEZONE = 'UTC';")
                        return@bufferedResultSetQuery connection
                            .createStatement()
                            .executeQuery(
                                String.format(
                                    "SELECT * FROM \"%s\".\"%s\" ORDER BY \"%s\" ASC;",
                                    schema,
                                    tableName,
                                    JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
                                )
                            )
                    }
            },
            { queryResult: ResultSet -> SnowflakeSourceOperations().rowToJson(queryResult) }
        )
    }

    // for each test we create a new schema in the database. run the test in there and then remove
    // it.
    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val schemaName = addRandomSuffix("integration_test", "_", 5)
        val createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName)
        TEST_SCHEMAS.add(schemaName)

        this.config = Jsons.clone<JsonNode>(staticConfig)
        (config as ObjectNode?)!!.put("schema", schemaName)

        dataSource =
            SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
        database = SnowflakeDatabaseUtils.getDatabase(dataSource)
        database.execute(createSchemaQuery)
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        testSchemas.add(config["schema"].asText())
        for (schema in testSchemas) {
            // we need to wrap namespaces in quotes, but that means we have to manually upcase them.
            // thanks, v1 destinations!
            // this probably doesn't actually work, because v1 destinations are mangling namespaces
            // and names
            // but it's approximately correct and maybe works for some things.
            val mangledSchema = schema.uppercase(Locale.getDefault())
            val dropSchemaQuery = String.format("DROP SCHEMA IF EXISTS \"%s\"", mangledSchema)
            database.execute(dropSchemaQuery)
        }

        close(dataSource)
    }

    @Disabled("See README for why this test is disabled")
    @Test
    @Throws(Exception::class)
    fun testCheckWithNoTextSchemaPermissionConnection() {
        // Config to user (creds) that has no permission to schema
        val config = deserialize(readFile(Path.of("secrets/config_no_text_schema_permission.json")))

        val standardCheckConnectionOutput = runCheck(config)

        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            standardCheckConnectionOutput.status
        )
        AssertionsForClassTypes.assertThat(standardCheckConnectionOutput.message)
            .contains(NO_USER_PRIVILEGES_ERR_MSG)
    }

    @Test
    @Throws(Exception::class)
    fun testCheckIpNotInWhiteListConnection() {
        // Config to user(creds) that has no warehouse assigned
        val config =
            deserialize(readFile(Path.of("secrets/insert_ip_not_in_whitelist_config.json")))

        val standardCheckConnectionOutput = runCheck(config)

        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            standardCheckConnectionOutput.status
        )
        AssertionsForClassTypes.assertThat(standardCheckConnectionOutput.message)
            .contains(IP_NOT_IN_WHITE_LIST_ERR_MSG)
    }

    @Test
    fun testBackwardCompatibilityAfterAddingOauth() {
        val deprecatedStyleConfig: JsonNode = Jsons.clone<JsonNode>(config)
        val password = deprecatedStyleConfig["credentials"]["password"]

        (deprecatedStyleConfig as ObjectNode).remove("credentials")
        deprecatedStyleConfig.set<JsonNode>("password", password)

        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.SUCCEEDED,
            runCheckWithCatchedException(deprecatedStyleConfig)
        )
    }

    @Test
    @Throws(Exception::class)
    fun testCheckWithKeyPairAuth() {
        val credentialsJsonString = deserialize(readFile(Path.of("secrets/config_key_pair.json")))
        val check =
            SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).check(credentialsJsonString)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check!!.status)
    }

    /** This test is disabled because it is very slow, and should only be run manually for now. */
    @Disabled
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSyncWithBillionRecords(messagesFilename: String, catalogFilename: String) {
        val catalog = deserialize(readResource(catalogFilename), AirbyteCatalog::class.java)
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages: List<AirbyteMessage> =
            readResource(messagesFilename)
                .lines()
                .map { record: String -> deserialize(record, AirbyteMessage::class.java) }
                .toList()

        val largeNumberRecords =
            Collections.nCopies(15000000, messages)
                .stream()
                .flatMap { obj: List<AirbyteMessage> -> obj.stream() }
                .collect(Collectors.toList())

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, largeNumberRecords, configuredCatalog, false)
    }

    companion object {
        private val NAME_TRANSFORMER: NamingConventionTransformer = SnowflakeSQLNameTransformer()
        @JvmStatic
        protected val NO_ACTIVE_WAREHOUSE_ERR_MSG: String =
            "No active warehouse selected in the current session.  Select an active warehouse with the 'use warehouse' command."

        @JvmStatic
        protected val NO_USER_PRIVILEGES_ERR_MSG: String =
            "Encountered Error with Snowflake Configuration: Current role does not have permissions on the target schema please verify your privileges"

        @JvmStatic
        protected val IP_NOT_IN_WHITE_LIST_ERR_MSG: String =
            "is not allowed to access Snowflake. Contact your local security administrator"
    }
}
