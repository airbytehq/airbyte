/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.DSLContextFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer
import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import java.util.stream.Collectors
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.SQLDialect

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
abstract class SshPostgresDestinationAcceptanceTest : AbstractPostgresDestinationAcceptanceTest() {
    private var testdb: PostgresTestDatabase? = null
    private var bastion: SshBastionContainer? = null

    abstract val tunnelMethod: SshTunnel.TunnelMethod

    @Throws(Exception::class)
    override fun getConfig(): JsonNode {
        // Here we use inner address because the tunnel is created inside the connector's container.
        return testdb!!
            .integrationTestConfigBuilder()
            .with("tunnel_method", bastion!!.getTunnelMethod(tunnelMethod, true)!!)
            .with("schema", "public")
            .withoutSsl()
            .build()
    }

    @Throws(Exception::class)
    override fun retrieveRecordsFromTable(tableName: String, schemaName: String): List<JsonNode> {
        // Here we DO NOT use the inner address because the tunnel is created in the integration
        // test's java
        // process.
        val config: JsonNode =
            testdb!!
                .integrationTestConfigBuilder()
                .with("tunnel_method", bastion!!.getTunnelMethod(tunnelMethod, false)!!)
                .with("schema", "public")
                .withoutSsl()
                .build()
        (config as ObjectNode).putObject(SshTunnel.CONNECTION_OPTIONS_KEY)
        return SshTunnel.sshWrap<List<JsonNode>>(
            config,
            JdbcUtils.HOST_LIST_KEY,
            JdbcUtils.PORT_LIST_KEY
        ) { mangledConfig: JsonNode ->
            getDatabaseFromConfig(mangledConfig).query<List<JsonNode>> { ctx: DSLContext ->
                ctx.execute("set time zone 'UTC';")
                ctx.fetch(
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
    }

    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        testdb =
            PostgresTestDatabase.`in`(
                PostgresTestDatabase.BaseImage.POSTGRES_13,
                PostgresTestDatabase.ContainerModifier.NETWORK
            )
        bastion = SshBastionContainer()
        bastion!!.initAndStartBastion(testdb!!.container.network!!)
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        testdb!!.close()
        bastion!!.stopAndClose()
    }

    override fun getTestDb(): PostgresTestDatabase {
        return testdb!!
    }

    companion object {
        private fun getDatabaseFromConfig(config: JsonNode): Database {
            return Database(
                create(
                    config.get(JdbcUtils.USERNAME_KEY).asText(),
                    config.get(JdbcUtils.PASSWORD_KEY).asText(),
                    DatabaseDriver.POSTGRESQL.driverClassName,
                    String.format(
                        DatabaseDriver.POSTGRESQL.urlFormatString,
                        config.get(JdbcUtils.HOST_KEY).asText(),
                        config.get(JdbcUtils.PORT_KEY).asInt(),
                        config.get(JdbcUtils.DATABASE_KEY).asText()
                    ),
                    SQLDialect.POSTGRES
                )
            )
        }
    }
}
