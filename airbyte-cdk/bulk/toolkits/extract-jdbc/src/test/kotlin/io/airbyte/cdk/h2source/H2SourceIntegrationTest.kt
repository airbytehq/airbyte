/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.h2source

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.ssh.SshBastionContainer
import io.airbyte.cdk.testcontainers.DOCKER_HOST_FROM_WITHIN_CONTAINER
import java.sql.Connection
import java.sql.Statement
import org.junit.jupiter.api.Test
import org.testcontainers.Testcontainers

class H2SourceIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("h2source/expected-spec.json")
    }

    @Test
    fun testCheckFailBadConfig() {
        SyncsTestFixture.testCheck(
            configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = -1
                    database = ""
                },
            expectedFailure = "Could not connect with provided configuration",
        )
    }

    @Test
    fun testCheckFailNoDatabase() {
        H2TestFixture().use { h2: H2TestFixture ->
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database + "_garbage"
                }
            SyncsTestFixture.testCheck(configPojo, "Connection failure: Database does not exist")
        }
    }

    @Test
    fun testCheckFailNoTables() {
        H2TestFixture().use { h2: H2TestFixture ->
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                }
            SyncsTestFixture.testCheck(configPojo, "Discovered zero tables")
        }
    }

    @Test
    fun testCheckSuccess() {
        H2TestFixture().use { h2: H2TestFixture ->
            h2.createConnection().use(Companion::prelude)
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                }
            SyncsTestFixture.testCheck(configPojo)
        }
    }

    @Test
    fun testCheckSshTunnel() {
        H2TestFixture().use { h2: H2TestFixture ->
            h2.createConnection().use(Companion::prelude)
            Testcontainers.exposeHostPorts(h2.port)
            SshBastionContainer(tunnelingToHostPort = h2.port).use { ssh: SshBastionContainer ->
                val configPojo =
                    H2SourceConfigurationSpecification().apply {
                        host =
                            DOCKER_HOST_FROM_WITHIN_CONTAINER // required only because of container
                        port = h2.port
                        database = h2.database
                    }
                configPojo.setTunnelMethodValue(ssh.outerKeyAuthTunnelMethod)
                SyncsTestFixture.testCheck(configPojo)
                configPojo.setTunnelMethodValue(ssh.outerPasswordAuthTunnelMethod)
                SyncsTestFixture.testCheck(configPojo)
            }
        }
    }

    @Test
    fun testDiscover() {
        H2TestFixture().use { h2: H2TestFixture ->
            h2.createConnection().use(Companion::prelude)
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                }
            SyncsTestFixture.testDiscover(configPojo, "h2source/expected-cursor-catalog.json")
        }
    }

    @Test
    fun testDiscoverFakeCdc() {
        H2TestFixture().use { h2: H2TestFixture ->
            h2.createConnection().use(Companion::prelude)
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                    setCursorMethodValue(CdcCursor)
                }
            SyncsTestFixture.testDiscover(configPojo, "h2source/expected-fake-cdc-catalog.json")
        }
    }

    @Test
    fun testReadStreams() {
        H2TestFixture().use { h2: H2TestFixture ->
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                    resumablePreferred = true
                }
            SyncsTestFixture.testSyncs(
                configPojo,
                h2::createConnection,
                Companion::prelude,
                "h2source/expected-cursor-catalog.json",
                "h2source/cursor-catalog.json",
                SyncsTestFixture.AfterRead.Companion.fromExpectedMessages(
                    "h2source/expected-messages-stream-cold-start.json",
                ),
                SyncsTestFixture.AfterRead.Companion.fromExpectedMessages(
                    "h2source/expected-messages-stream-warm-start.json",
                ),
            )
        }
    }

    @Test
    fun testReadStreamStateTooFarAhead() {
        H2TestFixture().use { h2: H2TestFixture ->
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                    resumablePreferred = true
                }
            SyncsTestFixture.testReads(
                configPojo,
                h2::createConnection,
                Companion::prelude,
                "h2source/incremental-only-catalog.json",
                "h2source/state-too-far-ahead.json",
                SyncsTestFixture.AfterRead.Companion.fromExpectedMessages(
                    "h2source/expected-messages-stream-too-far-ahead.json",
                ),
            )
        }
    }

    @Test
    fun testReadBadCatalog() {
        H2TestFixture().use { h2: H2TestFixture ->
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                    resumablePreferred = true
                }
            SyncsTestFixture.testReads(
                configPojo,
                h2::createConnection,
                Companion::prelude,
                "h2source/bad-catalog.json",
                initialStateResource = null,
                SyncsTestFixture.AfterRead.Companion.fromExpectedMessages(
                    "h2source/expected-messages-stream-bad-catalog.json",
                ),
            )
        }
    }

    @Test
    fun testEmptyTable() {
        H2TestFixture().use { h2: H2TestFixture ->
            val configPojo =
                H2SourceConfigurationSpecification().apply {
                    port = h2.port
                    database = h2.database
                    resumablePreferred = true
                }
            SyncsTestFixture.testReads(
                configPojo,
                h2::createConnection,
                Companion::emptyTablePrelude,
                "h2source/incremental-only-catalog.json",
                null,
                SyncsTestFixture.AfterRead.Companion.fromExpectedMessages(
                    "h2source/empty.json",
                ),
            )
        }
    }

    companion object {
        @JvmStatic
        fun prelude(connection: Connection) {
            for (sql in listOf(CREATE_KV, INSERT_KV, CREATE_EVENTS, INSERT_EVENTS)) {
                connection.createStatement().use { stmt: Statement -> stmt.execute(sql) }
            }
        }

        @JvmStatic
        fun emptyTablePrelude(connection: Connection) {
            connection.createStatement().use { stmt: Statement -> stmt.execute(CREATE_EVENTS) }
        }

        const val CREATE_KV = "CREATE TABLE kv (k INT PRIMARY KEY, v VARCHAR(60));"
        const val INSERT_KV = "INSERT INTO kv (k, v) VALUES (1, 'foo'), (2, 'bar'), (3, NULL);"
        const val CREATE_EVENTS =
            "CREATE TABLE events (" +
                "id UUID PRIMARY KEY," +
                "ts TIMESTAMP WITH TIME ZONE NOT NULL," +
                "msg VARCHAR(60));"
        const val INSERT_EVENTS =
            "INSERT INTO events (id, ts, msg) VALUES " +
                "('cc449902-30da-5ea8-c4d3-02732e5bfce9', '2024-04-29T00:00:00-04:00', 'bar')," +
                "('dd55aa13-41eb-6fb4-d5e4-13843f6c0dfa', '2024-04-30T00:00:00-04:00', NULL);"
    }
}
