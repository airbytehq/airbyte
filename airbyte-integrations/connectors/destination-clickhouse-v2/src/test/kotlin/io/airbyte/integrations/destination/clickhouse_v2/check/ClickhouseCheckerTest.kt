/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.check

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.insert.InsertResponse
import com.clickhouse.data.ClickHouseFormat
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
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

    @MockK lateinit var clientFactory: RawClickHouseClientFactory

    @MockK lateinit var insertResponse: InsertResponse

    private lateinit var checker: ClickhouseChecker

    @BeforeEach
    fun setup() {
        every { clientFactory.make(any()) } returns client
        every { client.execute(any()) } returns mockk(relaxed = true)
        every { insertResponse.writtenRows } returns 1
        every { client.insert(any(), any<InputStream>(), any()) } returns
            CompletableFuture.completedFuture(insertResponse)
        every { clock.millis() } returns Fixtures.MILLIS
        checker = ClickhouseChecker(clock, clientFactory)
    }

    @Test
    fun `check happy path - creates check table and inserts data`() {
        checker.check(Fixtures.config)

        verify {
            client.execute(
                "CREATE TABLE IF NOT EXISTS ${Fixtures.config.database}.${checker.tableName} (test UInt8) ENGINE = MergeTree ORDER BY ()"
            )
        }
        verify {
            client.insert(checker.tableName, any<InputStream>(), ClickHouseFormat.JSONEachRow)
        }
    }

    @Test
    fun `check happy path - table name differs between instantiations to prevent collision`() {
        val time1 = 123L
        every { clock.millis() } returns time1
        val checker1 = ClickhouseChecker(clock, clientFactory)
        val time2 = 3416L
        every { clock.millis() } returns time2
        val checker2 = ClickhouseChecker(clock, clientFactory)
        val time3 = 1236L
        every { clock.millis() } returns time3
        val checker3 = ClickhouseChecker(clock, clientFactory)

        assertNotEquals(checker1.tableName, checker2.tableName)
        assertNotEquals(checker1.tableName, checker3.tableName)
        assertNotEquals(checker2.tableName, checker3.tableName)
    }

    @Test
    fun `check table creation failure`() {
        val exception = Exception("blam")
        every { client.execute(any()) } throws exception

        val caught = assertThrows<Exception> { checker.check(Fixtures.config) }
        assertEquals(exception, caught)
    }

    @Test
    fun `check insert data failure`() {
        val exception = Exception("blam")
        every { client.insert(any(), any<InputStream>(), any()) } throws exception

        val caught = assertThrows<Exception> { checker.check(Fixtures.config) }
        assertEquals(exception, caught)
    }

    @Test
    fun `cleanup happy path - drops the check table`() {
        checker.cleanup(Fixtures.config)

        verify {
            client.execute("DROP TABLE IF EXISTS ${Fixtures.config.database}.${checker.tableName}")
        }
    }

    @Test
    fun `cleanup drop table failure`() {
        val exception = Exception("blam")
        every { client.execute(any()) } throws exception

        val caught = assertThrows<Exception> { checker.cleanup(Fixtures.config) }
        assertEquals(exception, caught)
    }

    object Fixtures {
        const val MILLIS = 1234L

        val config =
            ClickhouseConfiguration(
                "hostname",
                "port",
                "protocol",
                "database",
                "username",
                "password",
            )
    }
}
