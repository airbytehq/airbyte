/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.SshBastionContainer
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.OracleContainer

private val log = KotlinLogging.logger {}

class OracleSourceDatatypeIntegrationTest {

    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }

    /** This test ensures that the contents of the two resources stay in sync. */
    @Test
    fun testConfiguredCatalogHasAllStreams() {
        val catalog: AirbyteCatalog = SyncsTestFixture.catalogFromResource("expected-catalog.json")
        val configuredCatalog: ConfiguredAirbyteCatalog =
            SyncsTestFixture.configuredCatalogFromResource("configured-catalog.json")
        val streamMap: Map<AirbyteStreamNameNamespacePair, AirbyteStream> =
            catalog.streams.associateBy(AirbyteStreamNameNamespacePair::fromAirbyteStream)
        for (cs in configuredCatalog.streams) {
            Assertions.assertEquals(
                streamMap[AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(cs)],
                cs.stream
            )
        }
    }

    @Test
    @Timeout(value = 300) // A high timeout value is required for Apple Silicon + colima.
    fun testSyncs() {
        SyncsTestFixture.testSyncs(
            config(),
            { connectionFactory.get() }, // stay lazy
            ::prelude,
            "expected-catalog.json",
            "configured-catalog.json",
            // TODO add READs
            )
        SshBastionContainer(dbContainer.network).use { sshBastionContainer: SshBastionContainer ->
            log.info { "testing key auth" }
            SyncsTestFixture.testCheck(
                config().apply {
                    setTunnelMethodValue(sshBastionContainer.outerKeyAuthTunnelMethod)
                }
            )
            log.info { "testing password auth" }
            SyncsTestFixture.testCheck(
                config().apply {
                    setTunnelMethodValue(sshBastionContainer.outerPasswordAuthTunnelMethod)
                }
            )
        }
    }

    companion object {

        lateinit var dbContainer: OracleContainer

        fun config(): OracleSourceConfigurationJsonObject =
            OracleContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(OracleSourceConfigurationFactory().make(config()))
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300) // A high timeout value is required for Apple Silicon + colima.
        fun startTestContainer() {
            dbContainer =
                OracleContainerFactory()
                    .exclusive(
                        "gvenzl/oracle-free:latest-faststart",
                        OracleContainerFactory.withNetwork
                    )
        }

        fun prelude(connection: Connection) {
            for (case in OracleDatatypesTestFixture.testCases) {
                for (sql in case.sqlStatements) {
                    log.info { "executing $sql" }
                    connection.createStatement().use { stmt -> stmt.execute(sql) }
                }
            }
        }
    }
}
