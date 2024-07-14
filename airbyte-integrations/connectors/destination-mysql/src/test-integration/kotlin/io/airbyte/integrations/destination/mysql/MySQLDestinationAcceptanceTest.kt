/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.DSLContextFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.cdk.integrations.util.HostPortResolver.resolveHost
import io.airbyte.cdk.integrations.util.HostPortResolver.resolvePort
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.protocol.models.v0.*
import java.sql.SQLException
import java.time.Instant
import java.util.concurrent.TimeUnit
import java.util.function.Function
import java.util.stream.Collectors
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.SQLDialect
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

@Disabled
open class MySQLDestinationAcceptanceTest : JdbcDestinationAcceptanceTest() {
    protected var db: MySQLContainer<*>? = null
    private val namingResolver: StandardNameTransformer = MySQLNameTransformer()

    override val imageName: String
        get() = "airbyte/destination-mysql:dev"

    override fun implementsNamespaces(): Boolean {
        return true
    }

    override fun getTestDataComparator(): TestDataComparator {
        return MySqlTestDataComparator()
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

    override fun getConfig(): JsonNode {
        return getConfigFromTestContainer(db!!)
    }

    private val configForBareMetalConnection: JsonNode
        /**
         * [.getConfig] returns a config with host/port set to the in-docker values. This works for
         * running the destination-mysql container, but we have some tests which run the destination
         * code directly from the JUnit process. These tests need to connect using the "normal"
         * host/port.
         */
        get() =
            (getConfig() as ObjectNode)
                .put(JdbcUtils.HOST_KEY, db!!.host)
                .put(JdbcUtils.PORT_KEY, db!!.firstMappedPort)

    override fun getFailCheckConfig(): JsonNode? {
        val config = getConfig() as ObjectNode
        config.put(JdbcUtils.PASSWORD_KEY, "wrong password")
        return config
    }

    override fun getDefaultSchema(config: JsonNode): String? {
        if (config.get(JdbcUtils.DATABASE_KEY) == null) {
            return null
        }
        return config.get(JdbcUtils.DATABASE_KEY).asText()
    }

    @Throws(Exception::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
            .stream()
            .map<JsonNode>(
                Function<JsonNode, JsonNode> { r: JsonNode ->
                    r.get(JavaBaseConstants.COLUMN_NAME_DATA)
                }
            )
            .collect(Collectors.toList<JsonNode>())
    }

    @Throws(SQLException::class)
    private fun retrieveRecordsFromTable(tableName: String, schemaName: String): List<JsonNode> {
        val dslContext =
            create(
                db!!.username,
                db!!.password,
                db!!.driverClassName,
                String.format(
                    DatabaseDriver.MYSQL.urlFormatString,
                    db!!.host,
                    db!!.firstMappedPort,
                    db!!.databaseName
                ),
                SQLDialect.MYSQL
            )
        return Database(dslContext).query<List<JsonNode>> { ctx: DSLContext? ->
            ctx!!
                .fetch(
                    String.format(
                        "SELECT * FROM %s.%s ORDER BY %s ASC;",
                        schemaName,
                        tableName,
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT
                    )
                )
                .stream()
                .map<JsonNode> { record: Record -> this.getJsonFromRecord(record) }
                .collect(Collectors.toList<JsonNode>())
        }!!
    }

    @Throws(Exception::class)
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun retrieveNormalizedRecords(
        testEnv: TestDestinationEnv?,
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        val tableName = namingResolver.getIdentifier(streamName!!)
        val schema = namingResolver.getIdentifier(namespace!!)
        return retrieveRecordsFromTable(tableName, schema)
    }

    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        db = MySQLContainer("mysql:8.0")
        db!!.start()
        configureTestContainer(db!!)
    }

    override fun tearDown(testEnv: TestDestinationEnv) {
        db!!.stop()
        db!!.close()
    }

    @Test
    @Throws(Exception::class)
    override fun testCustomDbtTransformations() {
        // We need to create view for testing custom dbt transformations
        executeQuery(db, "GRANT CREATE VIEW ON *.* TO " + db!!.username + "@'%';")
        super.testCustomDbtTransformations()
    }

    @Test
    @Throws(Exception::class)
    fun testJsonSync() {
        val catalogAsText =
            """{
  "streams": [
    {
      "name": "exchange_rate",
      "json_schema": {
        "properties": {
          "id": {
            "type": "integer"
          },
          "data": {
            "type": "string"
          }        }
      }
    }
  ]
}
"""

        val catalog = deserialize(catalogAsText, AirbyteCatalog::class.java)
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages: List<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put(
                                            "data",
                                            "{\"name\":\"Conferência Faturamento - Custo - Taxas - Margem - Resumo ano inicial até -2\",\"description\":null}"
                                        )
                                        .build()
                                )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage().withData(jsonNode(ImmutableMap.of("checkpoint", 2)))
                    )
            )

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema)
    }

    @Test
    override fun testLineBreakCharacters() {
        // overrides test with a no-op until we handle full UTF-8 in the destination
    }

    protected fun assertSameValue(expectedValue: JsonNode, actualValue: JsonNode) {
        if (expectedValue.isBoolean) {
            // Boolean in MySQL are stored as TINYINT (0 or 1) so we force them to boolean values
            // here
            Assertions.assertEquals(expectedValue.asBoolean(), actualValue.asBoolean())
        } else {
            Assertions.assertEquals(expectedValue, actualValue)
        }
    }

    // Something is very weird in our connection check code. A wrong password takes >1 minute to
    // return.
    // TODO investigate why invalid creds take so long to detect
    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    @Test
    fun testCheckIncorrectPasswordFailure() {
        val config: JsonNode =
            (configForBareMetalConnection as ObjectNode).put(JdbcUtils.PASSWORD_KEY, "fake")
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        assertStringContains(status.message, "State code: 28000; Error code: 1045;")
    }

    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    @Test
    fun testCheckIncorrectUsernameFailure() {
        val config: JsonNode =
            (configForBareMetalConnection as ObjectNode).put(JdbcUtils.USERNAME_KEY, "fake")
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        assertStringContains(status.message, "State code: 28000; Error code: 1045;")
    }

    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    @Test
    fun testCheckIncorrectHostFailure() {
        val config: JsonNode =
            (configForBareMetalConnection as ObjectNode).put(JdbcUtils.HOST_KEY, "localhost2")
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        assertStringContains(status.message, "State code: 08S01;")
    }

    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    @Test
    fun testCheckIncorrectPortFailure() {
        val config: JsonNode =
            (configForBareMetalConnection as ObjectNode).put(JdbcUtils.PORT_KEY, "0000")
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        assertStringContains(status.message, "State code: 08S01;")
    }

    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    @Test
    fun testCheckIncorrectDataBaseFailure() {
        val config: JsonNode =
            (configForBareMetalConnection as ObjectNode).put(
                JdbcUtils.DATABASE_KEY,
                "wrongdatabase"
            )
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        assertStringContains(status.message, "State code: 42000; Error code: 1049;")
    }

    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    @Test
    open fun testUserHasNoPermissionToDataBase() {
        executeQuery(
            db!!,
            "create user '" +
                USERNAME_WITHOUT_PERMISSION +
                "'@'%' IDENTIFIED BY '" +
                PASSWORD_WITHOUT_PERMISSION +
                "';\n"
        )
        val config: JsonNode =
            (configForBareMetalConnection as ObjectNode).put(
                JdbcUtils.USERNAME_KEY,
                USERNAME_WITHOUT_PERMISSION
            )
        (config as ObjectNode).put(JdbcUtils.PASSWORD_KEY, PASSWORD_WITHOUT_PERMISSION)
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        assertStringContains(status.message, "State code: 42000; Error code: 1044;")
    }

    /**
     * Legacy mysql normalization is broken, and uses the FLOAT type for numbers. This rounds off
     * e.g. 12345.678 to 12345.7. We can fix this in DV2, but will not fix legacy normalization. As
     * such, disabling the test case.
     */
    @Disabled(
        "MySQL normalization uses the wrong datatype for numbers. This will not be fixed, because we intend to replace normalization with DV2."
    )
    @Throws(Exception::class)
    override fun testDataTypeTestWithNormalization(
        messagesFilename: String,
        catalogFilename: String,
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ) {
        super.testDataTypeTestWithNormalization(
            messagesFilename,
            catalogFilename,
            testCompatibility
        )
    }

    companion object {
        const val USERNAME_WITHOUT_PERMISSION: String = "new_user"
        const val PASSWORD_WITHOUT_PERMISSION: String = "new_password"

        fun getConfigFromTestContainer(db: MySQLContainer<*>): ObjectNode {
            return jsonNode<ImmutableMap<Any, Any>>(
                ImmutableMap.builder<Any, Any>()
                    .put(JdbcUtils.HOST_KEY, resolveHost(db))
                    .put(JdbcUtils.USERNAME_KEY, db.username)
                    .put(JdbcUtils.PASSWORD_KEY, db.password)
                    .put(JdbcUtils.DATABASE_KEY, db.databaseName)
                    .put(JdbcUtils.PORT_KEY, resolvePort(db))
                    .put(JdbcUtils.SSL_KEY, false)
                    .build()
            )
                as ObjectNode
        }

        fun configureTestContainer(db: MySQLContainer<*>) {
            setLocalInFileToTrue(db)
            revokeAllPermissions(db)
            grantCorrectPermissions(db)
        }

        private fun setLocalInFileToTrue(db: MySQLContainer<*>?) {
            executeQuery(db, "set global local_infile=true")
        }

        private fun revokeAllPermissions(db: MySQLContainer<*>?) {
            executeQuery(db, "REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + db!!.username + "@'%';")
        }

        private fun grantCorrectPermissions(db: MySQLContainer<*>?) {
            executeQuery(
                db,
                "GRANT ALTER, CREATE, INSERT, INDEX, UPDATE, DELETE, SELECT, DROP ON *.* TO " +
                    db!!.username +
                    "@'%';"
            )
        }

        private fun executeQuery(db: MySQLContainer<*>?, query: String) {
            val dslContext =
                create(
                    "root",
                    "test",
                    db!!.driverClassName,
                    String.format(
                        DatabaseDriver.MYSQL.urlFormatString,
                        db.host,
                        db.firstMappedPort,
                        db.databaseName
                    ),
                    SQLDialect.MYSQL
                )
            try {
                Database(dslContext).query { ctx: DSLContext? -> ctx!!.execute(query) }
            } catch (e: SQLException) {
                throw RuntimeException(e)
            }
        }

        private fun assertStringContains(str: String, target: String) {
            Assertions.assertTrue(
                str.contains(target),
                "Expected message to contain \"$target\" but got $str"
            )
        }
    }
}
