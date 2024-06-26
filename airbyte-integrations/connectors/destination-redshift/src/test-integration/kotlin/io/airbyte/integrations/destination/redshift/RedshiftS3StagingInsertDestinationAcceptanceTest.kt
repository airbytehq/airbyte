/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.amazon.redshift.util.RedshiftTimestamp
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.ConnectionFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils.DATABASE_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.HOST_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.PASSWORD_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.PORT_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.USERNAME_KEY
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces.generate
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces.isOlderThan2Days
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.integrations.destination.redshift.RedshiftDestination.Companion.SSL_JDBC_PARAMETERS
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations
import java.nio.file.Path
import java.sql.Connection
import java.sql.SQLException
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField
import java.util.Optional
import java.util.stream.Collectors
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.impl.DSL
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Integration test testing [RedshiftDestination]. The default Redshift integration test credentials
 * contain S3 credentials - this automatically causes COPY to be selected.
 */
// these tests are not yet thread-safe, unlike the DV2 tests.
@Execution(ExecutionMode.SAME_THREAD)
@Disabled
class RedshiftS3StagingInsertDestinationAcceptanceTest : JdbcDestinationAcceptanceTest() {
    // config from which to create / delete schemas.
    private lateinit var baseConfig: JsonNode

    // config which refers to the schema that the test is being run in.
    // override the getter name, because the base class declares a getConfig method, which clashes.
    // Eventually we should just replace the super method with a native kotlin `abstract val`.
    @get:JvmName("getConfig_")
    protected lateinit var config: JsonNode
        @SuppressFBWarnings(
            "NP_NONNULL_RETURN_VIOLATION",
            "spotbugs doesn't like lateinit on non-private vars"
        )
        get
    private val namingResolver = RedshiftSQLNameTransformer()
    private val USER_WITHOUT_CREDS = addRandomSuffix("test_user", "_", 5)

    protected var database: Database? = null
        private set
    private lateinit var connection: Connection
    protected var testDestinationEnv: TestDestinationEnv? = null

    override val imageName: String
        get() = "airbyte/destination-redshift:dev"

    override fun getConfig(): JsonNode {
        return config
    }

    val staticConfig: JsonNode
        get() = deserialize(readFile(Path.of("secrets/config_staging.json")))

    override fun getFailCheckConfig(): JsonNode? {
        val invalidConfig: JsonNode = Jsons.clone<JsonNode>(config)
        (invalidConfig as ObjectNode).put("password", "wrong password")
        return invalidConfig
    }

    override fun getTestDataComparator(): TestDataComparator {
        return RedshiftTestDataComparator()
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

    override fun supportsInDestinationNormalization(): Boolean {
        return true
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
            .map { j: JsonNode -> j.get(COLUMN_NAME_DATA) }
            .collect(Collectors.toList())
    }

    override fun implementsNamespaces(): Boolean {
        return true
    }

    @Throws(Exception::class)
    override fun retrieveNormalizedRecords(
        testEnv: TestDestinationEnv?,
        @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        var tableName = namingResolver.getIdentifier(streamName!!)
        if (!tableName.startsWith("\"")) {
            // Currently, Normalization always quote tables identifiers
            tableName = "\"" + tableName + "\""
        }
        return retrieveRecordsFromTable(tableName, namespace)
    }

    @Throws(SQLException::class)
    private fun retrieveRecordsFromTable(tableName: String, schemaName: String?): List<JsonNode> {
        return database!!.query<List<JsonNode>> { ctx: DSLContext ->
            ctx.fetch(
                    String.format(
                        "SELECT * FROM %s.%s ORDER BY %s ASC;",
                        schemaName,
                        tableName,
                        COLUMN_NAME_EMITTED_AT
                    )
                )
                .stream()
                .map { record: Record ->
                    getJsonFromRecord(record) { value: Any ->
                        if (value is RedshiftTimestamp) {
                            // We can't just use rts.toInstant().toString(), because that will
                            // mangle historical
                            // dates (e.g. 1504-02-28...) because toInstant() just converts to epoch
                            // millis,
                            // which works _very badly_ for for very old dates.
                            // Instead, convert to a string and then parse that string.
                            // We can't just rts.toString(), because that loses the timezone...
                            // so instead we use getPostgresqlString and parse that >.>
                            // Thanks, redshift.
                            return@getJsonFromRecord Optional.of<String>(
                                ZonedDateTime.parse(
                                        value.postgresqlString,
                                        DateTimeFormatterBuilder()
                                            .appendPattern("yyyy-MM-dd HH:mm:ss")
                                            .optionalStart()
                                            .appendFraction(ChronoField.MILLI_OF_SECOND, 0, 9, true)
                                            .optionalEnd()
                                            .appendPattern("X")
                                            .toFormatter()
                                    )
                                    .withZoneSameInstant(ZoneOffset.UTC)
                                    .toString()
                            )
                        } else {
                            return@getJsonFromRecord Optional.empty<String>()
                        }
                    }
                }
                .collect(Collectors.toList<JsonNode>())
        }!!
    }

    // for each test we create a new schema in the database. run the test in there and then remove
    // it.
    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val schemaName = generate()
        val createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName)
        baseConfig = staticConfig
        database = createDatabase()
        removeOldNamespaces()
        database!!.query { ctx: DSLContext -> ctx.execute(createSchemaQuery) }
        val createUser =
            String.format(
                "create user %s with password '%s' SESSION TIMEOUT 60;",
                USER_WITHOUT_CREDS,
                baseConfig!!["password"].asText()
            )
        database!!.query { ctx: DSLContext -> ctx.execute(createUser) }
        val configForSchema: JsonNode = Jsons.clone<JsonNode>(baseConfig)
        (configForSchema as ObjectNode).put("schema", schemaName)
        TEST_SCHEMAS.add(schemaName)
        config = configForSchema
        testDestinationEnv = testEnv
    }

    private fun removeOldNamespaces() {
        val schemas: List<String>
        try {
            schemas =
                database!!
                    .query { ctx: DSLContext ->
                        ctx.fetch("SELECT schema_name FROM information_schema.schemata;")
                    }!!
                    .stream()
                    .map { record: Record -> record["schema_name"].toString() }
                    .toList()
        } catch (e: SQLException) {
            // if we can't fetch the schemas, just return.
            return
        }

        var schemasDeletedCount = 0
        for (schema in schemas) {
            if (isOlderThan2Days(schema)) {
                try {
                    database!!.query { ctx: DSLContext ->
                        ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", schema))
                    }
                    schemasDeletedCount++
                } catch (e: SQLException) {
                    LOGGER.error("Failed to delete old dataset: {}", schema, e)
                }
            }
        }
        LOGGER.info("Deleted {} old schemas.", schemasDeletedCount)
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        println("TEARING_DOWN_SCHEMAS: $testSchemas")
        database!!.query { ctx: DSLContext ->
            ctx.execute(
                String.format("DROP SCHEMA IF EXISTS %s CASCADE", config!!["schema"].asText())
            )
        }
        for (schema in testSchemas) {
            database!!.query { ctx: DSLContext ->
                ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", schema))
            }
        }
        database!!.query { ctx: DSLContext ->
            ctx.execute(String.format("drop user if exists %s;", USER_WITHOUT_CREDS))
        }
        RedshiftConnectionHandler.close(connection)
    }

    protected fun createDatabase(): Database {
        connection =
            create(
                baseConfig.get(USERNAME_KEY).asText(),
                baseConfig.get(PASSWORD_KEY).asText(),
                // ConnectionFactory.create() excepts a Map<String?, String?>
                // but SSL_JDBC_PARAMETERS is a Map<String, String>
                // so copy it to a new map :(
                HashMap(SSL_JDBC_PARAMETERS),
                String.format(
                    DatabaseDriver.REDSHIFT.urlFormatString,
                    baseConfig.get(HOST_KEY).asText(),
                    baseConfig.get(PORT_KEY).asInt(),
                    baseConfig.get(DATABASE_KEY).asText()
                )
            )

        return Database(DSL.using(connection))
    }

    override val maxRecordValueLimit: Int
        get() = RedshiftSqlOperations.REDSHIFT_VARCHAR_MAX_BYTE_SIZE

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(RedshiftS3StagingInsertDestinationAcceptanceTest::class.java)
    }
}
