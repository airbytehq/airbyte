/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.ContextQueryFunction
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.DSLContextFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.deserialize
import java.nio.file.Path
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import org.apache.commons.lang3.RandomStringUtils
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.SQLDialect
import org.junit.jupiter.api.Disabled

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 *
 * This class probably should extend [MySQLDestinationAcceptanceTest] to further reduce code
 * duplication though.
 */
@Disabled
abstract class SshMySQLDestinationAcceptanceTest : JdbcDestinationAcceptanceTest() {
    private val namingResolver: StandardNameTransformer = MySQLNameTransformer()
    private var schemaName: String? = null

    abstract val configFilePath: Path?

    override val imageName: String
        get() = "airbyte/destination-mysql:dev"

    override fun getConfig(): JsonNode {
        val config = configFromSecretsFile
        (config as ObjectNode).put(JdbcUtils.DATABASE_KEY, schemaName)
        return config
    }

    private val configFromSecretsFile: JsonNode
        get() = deserialize(readFile(configFilePath))

    override fun getFailCheckConfig(): JsonNode? {
        val clone: JsonNode = Jsons.clone<JsonNode>(getConfig())
        (clone as ObjectNode).put("password", "wrong password")
        return clone
    }

    @Throws(Exception::class)
    override fun retrieveRecords(
        env: TestDestinationEnv?,
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

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    @Throws(Exception::class)
    override fun retrieveNormalizedRecords(
        env: TestDestinationEnv?,
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        val tableName = namingResolver.getIdentifier(streamName!!)
        val schema =
            if (namespace != null) namingResolver.getIdentifier(namespace)
            else namingResolver.getIdentifier(schemaName!!)
        return retrieveRecordsFromTable(tableName, schema)
    }

    override fun getDefaultSchema(config: JsonNode): String? {
        if (config.get(JdbcUtils.DATABASE_KEY) == null) {
            return null
        }
        return config.get(JdbcUtils.DATABASE_KEY).asText()
    }

    @Throws(Exception::class)
    private fun retrieveRecordsFromTable(tableName: String, schemaName: String?): List<JsonNode> {
        val schema = schemaName ?: this.schemaName
        return SshTunnel.sshWrap(getConfig(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY) {
            mangledConfig: JsonNode ->
            getDatabaseFromConfig(mangledConfig)
                .query { ctx: DSLContext? ->
                    ctx!!.fetch(
                        String.format(
                            "SELECT * FROM %s.%s ORDER BY %s ASC;",
                            schema,
                            tableName.lowercase(Locale.getDefault()),
                            JavaBaseConstants.COLUMN_NAME_EMITTED_AT
                        )
                    )
                }!!
                .map<JsonNode> { record: Record ->
                    this@SshMySQLDestinationAcceptanceTest.getJsonFromRecord(record)
                }
        }
    }

    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        schemaName = RandomStringUtils.randomAlphabetic(8).lowercase(Locale.getDefault())
        val config = getConfig()
        SshTunnel.sshWrap(config, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY) {
            mangledConfig: JsonNode ->
            getDatabaseFromConfig(mangledConfig)
                .query(
                    ContextQueryFunction { ctx: DSLContext? ->
                        ctx!!.fetch(String.format("CREATE DATABASE %s;", schemaName))
                    }
                )
        }
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        SshTunnel.sshWrap(getConfig(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY) {
            mangledConfig: JsonNode ->
            getDatabaseFromConfig(mangledConfig)
                .query(
                    ContextQueryFunction { ctx: DSLContext? ->
                        ctx!!.fetch(String.format("DROP DATABASE %s", schemaName))
                    }
                )
        }
    }

    /**
     * Disabled for the same reason as in [MySQLDestinationAcceptanceTest]. But for some reason,
     * this class doesn't extend that one so we have to do it again.
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
        private fun getDatabaseFromConfig(config: JsonNode): Database {
            val dslContext =
                create(
                    config.get(JdbcUtils.USERNAME_KEY).asText(),
                    config.get(JdbcUtils.PASSWORD_KEY).asText(),
                    DatabaseDriver.MYSQL.driverClassName,
                    String.format(
                        "jdbc:mysql://%s:%s",
                        config.get(JdbcUtils.HOST_KEY).asText(),
                        config.get(JdbcUtils.PORT_KEY).asText()
                    ),
                    SQLDialect.MYSQL
                )
            return Database(dslContext)
        }
    }
}
