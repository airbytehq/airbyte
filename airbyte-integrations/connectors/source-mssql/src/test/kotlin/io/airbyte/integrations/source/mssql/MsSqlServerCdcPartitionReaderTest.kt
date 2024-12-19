package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.*
import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.cdk.util.Jsons
import org.apache.kafka.connect.source.SourceRecord
import java.sql.Connection
import java.sql.Statement
import java.time.Instant
import kotlin.random.Random
import kotlin.random.nextInt
import io.airbyte.cdk.ssh.TunnelSession
import io.debezium.connector.sqlserver.Lsn
import io.debezium.connector.sqlserver.SqlServerConnector
import io.debezium.connector.sqlserver.TxLogPosition
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.shaded.com.google.common.collect.Maps
import java.util.*
import java.util.concurrent.atomic.AtomicInteger

class MsSqlServerCdcPartitionReaderTest :
        AbstractCdcPartitionReaderTest<TxLogPosition, MsSqlServercontainerWithCdc>(
            namespace = "test",
        ) {

        override fun createContainer(): MsSqlServercontainerWithCdc {
            val retVal = MsSqlServerContainerFactory.exclusive(MsSqlServerImage.SQLSERVER_2022, MsSqlServerContainerFactory.WithCdcAgent) as MsSqlServercontainerWithCdc
            retVal.config.schemas = arrayOf("test")
            return retVal
        }

        companion object {
            const val DOCKER_IMAGE_NAME = "mcr.microsoft.com/mssql/server:2022-latest"
            init {
                TestContainerFactory.register(DOCKER_IMAGE_NAME, ::MSSQLServerContainer)
            }
        }

        override fun MsSqlServercontainerWithCdc.createStream() {
            withStatement { it.execute("CREATE SCHEMA test") }
            withStatement { it.execute("CREATE TABLE test.tbl (id INT PRIMARY KEY IDENTITY, v INT)") }
            withStatement {it.execute(MsSqlServercontainerWithCdc.ENABLE_CDC_SQL_FMT.format("test", "tbl", "RANDOM_ROLE", "cdc_test_tbl"))}
            withWaitUntilMaxLsnAvailable(config)

        }

        override fun MsSqlServercontainerWithCdc.insert(vararg id: Int) {
            for (i in id) {
                withStatement { it.execute("INSERT INTO test.tbl (v) VALUES ($i)") }
            }
            waitForCdcNewRecords(id.size)
        }

        override fun MsSqlServercontainerWithCdc.update(vararg id: Int) {
            for (i in id) {
                withStatement { it.execute("UPDATE test.tbl SET v = ${i + 1} WHERE id = $i") }
            }
            waitForCdcNewRecords(id.size)
        }

        override fun MsSqlServercontainerWithCdc.delete(vararg id: Int) {
            for (i in id) {
                withStatement { it.execute("DELETE FROM test.tbl WHERE id = $i") }
            }
            waitForCdcNewRecords(id.size)
        }

        private fun <X> MsSqlServercontainerWithCdc.withStatement(fn: (Statement) -> X): X {
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config)).get().use { connection: Connection ->
                connection.createStatement().use {
                    val rs = it.executeQuery("select DB_NAME()")
                    rs.next()
                    log.info{"SGX dbName=${rs.getString(1)}"}
                }
                connection.createStatement().use { return fn(it) }
            }
        }

        private var lastRecordCount = 0
        private fun MsSqlServercontainerWithCdc.waitForCdcNewRecords(numNewRecords: Int) {
            var currentRecordCount: Int = lastRecordCount
            var retries = 0
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config)).get().use { connection: Connection ->
                connection.createStatement().use {
                    do {
                        Thread.sleep(1000)
                        log.info{"SGX waiting to see ${lastRecordCount + numNewRecords} CDC records. Currently seeing only $currentRecordCount on retry $retries"}
                        val rs = it.executeQuery("SELECT count(*) FROM cdc.cdc_test_tbl_ct")
                        rs.next()
                        currentRecordCount = rs.getInt(1)
                    } while (currentRecordCount < lastRecordCount + numNewRecords && retries++ < MsSqlServercontainerWithCdc.MAX_RETRIES)
                }
            }
            if (currentRecordCount < lastRecordCount + numNewRecords) {
                throw RuntimeException("Failed to wait for new records")
            } else {
                lastRecordCount = currentRecordCount

                return
            }
        }

        override fun getCdcOperations(): DebeziumOperations<TxLogPosition> {
            val config = MsSqlServerSourceConfigurationFactory().make(container.config)
            return MsSqlServerDebeziumOperations(JdbcConnectionFactory(config), config)
        }
    }

