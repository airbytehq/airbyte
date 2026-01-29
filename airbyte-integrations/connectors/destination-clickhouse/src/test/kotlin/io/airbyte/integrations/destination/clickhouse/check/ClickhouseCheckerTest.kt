/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.check

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.insert.InsertResponse
import com.clickhouse.data.ClickHouseFormat
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.destination.clickhouse.check.ClickhouseChecker.Constants.PROTOCOL
import io.airbyte.integrations.destination.clickhouse.check.ClickhouseChecker.Constants.PROTOCOL_ERR_MESSAGE
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import java.io.InputStream
import java.time.Clock
import java.util.concurrent.CompletableFuture
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ClickhouseCheckerTest {
    @MockK lateinit var clock: Clock

    @MockK lateinit var client: Client

    @MockK lateinit var insertResponse: InsertResponse

    private val config = Fixtures.config()

    private lateinit var checker: ClickhouseChecker

    @BeforeEach
    fun setup() {
        every { client.execute(any()) } returns mockk(relaxed = true)
        every { insertResponse.writtenRows } returns 1
        every { client.insert(any(), any<InputStream>(), any()) } returns
            CompletableFuture.completedFuture(insertResponse)
        every { clock.millis() } returns Fixtures.MILLIS
        checker = ClickhouseChecker(clock, config, client)
    }

    @Test
    fun `check happy path - creates check table and inserts data`() {
        checker.check()

        verify {
            client.execute(
                "CREATE TABLE IF NOT EXISTS ${config.database}.${checker.tableName} (test UInt8) ENGINE = MergeTree ORDER BY ()"
            )
        }
        verify {
            client.insert(
                "${config.database}.${checker.tableName}",
                any<InputStream>(),
                ClickHouseFormat.JSONEachRow
            )
        }
    }

    @Test
    fun `check happy path - table name differs between instantiations to prevent collision`() {
        every { clock.millis() } returns 123L
        val checker1 = ClickhouseChecker(clock, config, client)
        every { clock.millis() } returns 3416L
        val checker2 = ClickhouseChecker(clock, config, client)
        every { clock.millis() } returns 1236L
        val checker3 = ClickhouseChecker(clock, config, client)

        assertNotEquals(checker1.tableName, checker2.tableName)
        assertNotEquals(checker1.tableName, checker3.tableName)
        assertNotEquals(checker2.tableName, checker3.tableName)
    }

    @Test
    fun `check hostname format failure - http`() {
        val badConfig =
            Fixtures.config(hostname = "${ClickhouseChecker.Constants.PROTOCOL}://hostname")
        val badChecker = ClickhouseChecker(clock, badConfig, client)

        val caught = assertThrows<IllegalArgumentException> { badChecker.check() }
        assertEquals(ClickhouseChecker.Constants.PROTOCOL_ERR_MESSAGE, caught.message)
    }

    @Test
    fun `check hostname format failure - https`() {
        val badConfig = Fixtures.config(hostname = "https://hostname")
        val badChecker = ClickhouseChecker(clock, badConfig, client)

        val caught = assertThrows<IllegalArgumentException> { badChecker.check() }
        assertEquals(ClickhouseChecker.Constants.PROTOCOL_ERR_MESSAGE, caught.message)
    }

    @Test
    fun `check table creation failure`() {
        val exception = Exception("blam")
        every { client.execute(any()) } throws exception

        val caught = assertThrows<Exception> { checker.check() }
        assertEquals(exception, caught)
    }

    @Test
    fun `check insert data failure`() {
        val exception = Exception("blam")
        every { client.insert(any(), any<InputStream>(), any()) } throws exception

        val caught = assertThrows<Exception> { checker.check() }
        assertEquals(exception, caught)
    }

    @Test
    fun `cleanup happy path - drops the check table`() {
        checker.cleanup()

        verify { client.execute("DROP TABLE IF EXISTS ${config.database}.${checker.tableName}") }
    }

    @Test
    fun `cleanup drop table failure`() {
        val exception = Exception("blam")
        every { client.execute(any()) } throws exception

        val caught = assertThrows<Exception> { checker.cleanup() }
        assertEquals(exception, caught)
    }

    object Fixtures {
        const val MILLIS = 1234L

        fun config(
            hostname: String = "hostname",
            port: String = "port",
            protocol: String = "protocol",
            database: String = "test-database",
            username: String = "username",
            password: String = "password",
            enableJson: Boolean = false,
            recordWindow: Long = 42000,
        ): ClickhouseConfiguration =
            ClickhouseConfiguration(
                hostname = hostname,
                port = port,
                protocol = protocol,
                database = database,
                username = username,
                password = password,
                enableJson = enableJson,
                tunnelConfig = SshNoTunnelMethod,
                recordWindowSize = recordWindow,
            )
    }
}
