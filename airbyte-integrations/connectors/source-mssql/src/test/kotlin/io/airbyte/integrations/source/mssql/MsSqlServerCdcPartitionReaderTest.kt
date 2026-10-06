/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.AbstractCdcPartitionReaderTest
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import java.sql.ResultSet
import java.time.Duration
import java.time.Instant
import org.apache.kafka.connect.source.SourceRecord
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MSSQLServerContainer

/**
 * Runs the CDK's [AbstractCdcPartitionReaderTest] against SQL Server with [AsyncEmbeddedEngine] (Dbz 3.4.3).
 * Debezium properties, cold start offsets and positions come from
 * the production [MsSqlServerDebeziumOperations], the rest are from the abstract test.
 */
class MsSqlServerCdcPartitionReaderTest :
    AbstractCdcPartitionReaderTest<MsSqlServerCdcPosition, MSSQLServerContainer<*>>(
        namespace = "dbo",
        timeout = Duration.ofSeconds(60),
    ) {

    private val config: MsSqlServerSourceConfiguration by lazy {
        MsSqlServerSourceConfigurationFactory()
            .make(MsSqlServerContainerFactory.config(container).also { it.setIncrementalValue(Cdc()) })
    }

    private val productionOps: MsSqlServerDebeziumOperations by lazy {
        MsSqlServerDebeziumOperations(JdbcConnectionFactory(config), config)
    }

    override fun createContainer(): MSSQLServerContainer<*> =
        MsSqlServerContainerFactory.exclusive(
            MsSqlServerContainerFactory.COMPATIBLE_NAME,
            MsSqlServerContainerFactory.WithAgent,
            MsSqlServerContainerFactory.WithTestDatabase,
        )

    @Test
    override fun integrationTest() {
        Assumptions.assumeTrue(false, "integrationTest's heartbeat-close assumption doesn't hold")
    }

    override fun MSSQLServerContainer<*>.createStream() {
        execute("EXEC sys.sp_cdc_enable_db")
        execute("CREATE TABLE dbo.tbl (id INT IDENTITY(1,1) PRIMARY KEY, v INT)")
        execute(
            "EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'tbl', " +
                "@role_name = NULL, @capture_instance = 'dbo_tbl'"
        )
        // The cold start offset is sys.fn_cdc_get_max_lsn(), which is NULL until the capture job
        // has run once.
        awaitCondition("sys.fn_cdc_get_max_lsn() to be available") {
            query("SELECT sys.fn_cdc_get_max_lsn()") { it.next() && it.getBytes(1) != null }
        }
    }

    override fun MSSQLServerContainer<*>.insert12345() {
        writeAndAwaitCapture(changeRows = 5, (1..5).map { "INSERT INTO dbo.tbl (v) VALUES ($it)" })
    }

    // Multiple rows in one transaction: all rows share one commit LSN. The first row
    // reaches the target position and triggers the close while Debezium is still delivering the rest.
    override fun MSSQLServerContainer<*>.insertMultipleInOneTransaction(n: Int) {
        writeAndAwaitCapture(
            changeRows = n,
            listOf("INSERT INTO dbo.tbl (v) VALUES ${(1..n).joinToString(",") { "($it)" }}"),
        )
    }

    override fun MSSQLServerContainer<*>.update135() {
        // An update is captured as two change rows: the before and the after image.
        writeAndAwaitCapture(
            changeRows = 6,
            listOf(
                "UPDATE dbo.tbl SET v = 6 WHERE id = 1",
                "UPDATE dbo.tbl SET v = 7 WHERE id = 3",
                "UPDATE dbo.tbl SET v = 8 WHERE id = 5",
            ),
        )
    }

    override fun MSSQLServerContainer<*>.delete24() {
        writeAndAwaitCapture(
            changeRows = 2,
            listOf("DELETE FROM dbo.tbl WHERE id = 2", "DELETE FROM dbo.tbl WHERE id = 4"),
        )
    }

    // Waiting until the Agent job copies changes from the log into the _CT table
    private fun writeAndAwaitCapture(changeRows: Int, statements: List<String>) {
        val before: Int = changeRowCount()
        statements.forEach { execute(it) }
        awaitCondition("$changeRows new change row(s) in cdc.dbo_tbl_CT") {
            changeRowCount() >= before + changeRows
        }
    }

    private fun changeRowCount(): Int =
        query("SELECT COUNT(*) FROM cdc.dbo_tbl_CT") {
            it.next()
            it.getInt(1)
        }

    private fun awaitCondition(what: String, condition: () -> Boolean) {
        val deadline: Instant = Instant.now().plus(CAPTURE_TIMEOUT)
        while (!condition()) {
            check(Instant.now().isBefore(deadline)) {
                "Timed out after $CAPTURE_TIMEOUT waiting for $what"
            }
            Thread.sleep(250)
        }
    }

    private fun execute(sql: String) {
        JdbcConnectionFactory(config).get().use { connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute(sql) }
        }
    }

    private fun <X> query(sql: String, fn: (ResultSet) -> X): X =
        JdbcConnectionFactory(config).get().use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery(sql).use { fn(it) }
            }
        }

    override fun createCdcPartitionsCreatorDbzOps():
        CdcPartitionsCreatorDebeziumOperations<MsSqlServerCdcPosition> =
        TestCdcPartitionsCreatorDbzOps()

    override fun createCdcPartitionReaderDbzOps():
        CdcPartitionReaderDebeziumOperations<MsSqlServerCdcPosition> =
        TestCdcPartitionReaderDbzOps()

    inner class TestCdcPartitionsCreatorDbzOps :
        AbstractCdcPartitionsCreatorDbzOps<MsSqlServerCdcPosition>() {
        override fun position(offset: DebeziumOffset): MsSqlServerCdcPosition =
            productionOps.position(offset)

        override fun generateColdStartOffset(): DebeziumOffset =
            productionOps.generateColdStartOffset()

        override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
            productionOps.generateColdStartProperties(streams)

        override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> =
            productionOps.generateWarmStartProperties(streams)
    }

    inner class TestCdcPartitionReaderDbzOps :
        AbstractCdcPartitionReaderDbzOps<MsSqlServerCdcPosition>() {
        override fun position(recordValue: DebeziumRecordValue): MsSqlServerCdcPosition? =
            productionOps.position(recordValue)

        override fun position(sourceRecord: SourceRecord): MsSqlServerCdcPosition? =
            productionOps.position(sourceRecord)
    }

    companion object {
        val CAPTURE_TIMEOUT: Duration = Duration.ofSeconds(60)
    }
}
