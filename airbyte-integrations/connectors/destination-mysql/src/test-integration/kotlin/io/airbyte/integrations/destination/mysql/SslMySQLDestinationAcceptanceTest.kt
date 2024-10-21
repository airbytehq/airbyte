/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.DSLContextFactory.create
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.util.HostPortResolver.resolveHost
import io.airbyte.cdk.integrations.util.HostPortResolver.resolvePort
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.sql.SQLException
import java.util.function.Function
import java.util.stream.Collectors
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.SQLDialect
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

@Disabled
class SslMySQLDestinationAcceptanceTest : MySQLDestinationAcceptanceTest() {
    private var dslContext: DSLContext? = null
    private val namingResolver: StandardNameTransformer = MySQLNameTransformer()

    override fun getConfig(): JsonNode {
        return jsonNode<ImmutableMap<Any, Any>>(
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.HOST_KEY, resolveHost(db!!))
                .put(JdbcUtils.USERNAME_KEY, db!!.username)
                .put(JdbcUtils.PASSWORD_KEY, db!!.password)
                .put(JdbcUtils.DATABASE_KEY, db!!.databaseName)
                .put(JdbcUtils.PORT_KEY, resolvePort(db!!))
                .put(JdbcUtils.SSL_KEY, true)
                .build()
        )
    }

    override fun getFailCheckConfig(): JsonNode? {
        return jsonNode<ImmutableMap<Any, Any>>(
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.HOST_KEY, resolveHost(db!!))
                .put(JdbcUtils.USERNAME_KEY, db!!.username)
                .put(JdbcUtils.PASSWORD_KEY, "wrong password")
                .put(JdbcUtils.DATABASE_KEY, db!!.databaseName)
                .put(JdbcUtils.PORT_KEY, resolvePort(db!!))
                .put(JdbcUtils.SSL_KEY, false)
                .build()
        )
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

    @Test
    override fun testCustomDbtTransformations() {
        // We need to create view for testing custom dbt transformations
        executeQuery("GRANT CREATE VIEW ON *.* TO " + db!!.username + "@'%';")
        // overrides test with a no-op until https://github.com/dbt-labs/jaffle_shop/pull/8 is
        // merged
        // super.testCustomDbtTransformations();
    }

    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        super.setup(testEnv, TEST_SCHEMAS)

        dslContext =
            create(
                db!!.username,
                db!!.password,
                db!!.driverClassName,
                String.format(
                    "jdbc:mysql://%s:%s/%s?useSSL=true&requireSSL=true&verifyServerCertificate=false",
                    db!!.host,
                    db!!.firstMappedPort,
                    db!!.databaseName
                ),
                SQLDialect.DEFAULT
            )
    }

    override fun tearDown(testEnv: TestDestinationEnv) {
        db!!.stop()
        db!!.close()
    }

    @Throws(SQLException::class)
    private fun retrieveRecordsFromTable(tableName: String, schemaName: String): List<JsonNode> {
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

    private fun setLocalInFileToTrue() {
        executeQuery("set global local_infile=true")
    }

    private fun revokeAllPermissions() {
        executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + db!!.username + "@'%';")
    }

    private fun grantCorrectPermissions() {
        executeQuery(
            "GRANT ALTER, CREATE, INSERT, SELECT, DROP ON *.* TO " + db!!.username + "@'%';"
        )
    }

    private fun executeQuery(query: String) {
        val dslContext =
            create(
                "root",
                "test",
                db!!.driverClassName,
                String.format(
                    "jdbc:mysql://%s:%s/%s?useSSL=true&requireSSL=true&verifyServerCertificate=false",
                    db!!.host,
                    db!!.firstMappedPort,
                    db!!.databaseName
                ),
                SQLDialect.DEFAULT
            )
        try {
            Database(dslContext).query { ctx: DSLContext? -> ctx!!.execute(query) }
        } catch (e: SQLException) {
            throw RuntimeException(e)
        }
    }

    @Test
    override fun testUserHasNoPermissionToDataBase() {
        executeQuery(
            "create user '" +
                MySQLDestinationAcceptanceTest.Companion.USERNAME_WITHOUT_PERMISSION +
                "'@'%' IDENTIFIED BY '" +
                MySQLDestinationAcceptanceTest.Companion.PASSWORD_WITHOUT_PERMISSION +
                "';\n"
        )
        val config: JsonNode =
            (getConfig() as ObjectNode).put(
                JdbcUtils.USERNAME_KEY,
                MySQLDestinationAcceptanceTest.Companion.USERNAME_WITHOUT_PERMISSION
            )
        (config as ObjectNode).put(
            "password",
            MySQLDestinationAcceptanceTest.Companion.PASSWORD_WITHOUT_PERMISSION
        )
        val destination = MySQLDestination()
        val status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
    }
}
