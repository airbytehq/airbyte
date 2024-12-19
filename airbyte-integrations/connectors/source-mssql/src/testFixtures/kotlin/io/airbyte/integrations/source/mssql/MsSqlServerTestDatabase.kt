/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql

import com.google.common.collect.Sets
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.test.fixtures.legacy.TestDatabase
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCursorBasedReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.debezium.connector.sqlserver.Lsn
import org.apache.commons.lang3.RandomStringUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.testcontainers.containers.MSSQLServerContainer
import java.io.IOException
import java.io.UncheckedIOException
import java.sql.SQLException
import java.sql.Statement
import java.util.*
import java.util.concurrent.ConcurrentHashMap
import kotlin.collections.MutableMap
import kotlin.collections.MutableSet

open class MsSQLTestDatabase(container: MsSqlServercontainer) :
    TestDatabase<MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration>(container.realContainer) {
    enum class BaseImage(@JvmField val reference: String) {
        MSSQL_2022("mcr.microsoft.com/mssql/server:2022-latest"),
    }

    fun withCdc(): MsSQLTestDatabase {
        LOGGER.info("enabling CDC on database {} with id {}", databaseName, databaseId)
        executeSqls("EXEC sys.sp_cdc_enable_db;")
        LOGGER.info("CDC enabled on database {} with id {}", databaseName, databaseId)
        return this
    }

    private val CDC_INSTANCE_NAMES: MutableSet<String> = Sets.newConcurrentHashSet()

    fun withCdcForTable(schemaName: String, tableName: String, roleName: String) {
        withCdcForTable(schemaName, tableName, roleName, "${schemaName}_${tableName}")
    }

    open fun withCdcForTable(schemaName: String, tableName: String, roleName: String?, instanceName: String) {
        LOGGER.info(formatLogLine("enabling CDC for table {}.{} and role {}, instance {}"), schemaName, tableName, roleName, instanceName)
        val sqlRoleName = if (roleName == null) "NULL" else "N'$roleName'"
        var tryCount = 0
        while (tryCount < MAX_RETRIES) {
            try {
                Thread.sleep(1000)
                synchronized(container) {
                    LOGGER.info(
                        formatLogLine("Trying to enable CDC for table {}.{} and role {}, instance {}, try {}/{}"), schemaName, tableName, roleName,
                        instanceName, tryCount, MAX_RETRIES
                    )
                    executeSqls(getEnableCdcSql(schemaName, tableName, sqlRoleName, instanceName))
                }
                CDC_INSTANCE_NAMES.add(instanceName)
                withShortenedCapturePollingInterval()
            } catch (e: Exception) {
                if (!e.message!!.contains(RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT)) {
                    throw e
                }
                tryCount++
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
            tryCount++
        }
        throw RuntimeException(formatLogLine("failed to enable CDC for table $schemaName.$tableName within $MAX_RETRIES seconds"))
    }

    open fun withCdcDisabledForTable(schemaName: String, tableName: String, instanceName: String) {
        LOGGER.info(formatLogLine("disabling CDC for table {}.{}, instance {}"), schemaName, tableName, instanceName)
        if (!CDC_INSTANCE_NAMES.remove(instanceName)) {
            throw RuntimeException(formatLogLine("CDC was disabled for instance ") + instanceName)
        }
        synchronized(container) {
            executeSqls(getDisableCdcSql(schemaName, tableName, instanceName))
        }
    }

    fun withoutCdc(){
        CDC_INSTANCE_NAMES.clear()
        synchronized(container) {
            executeSqls(DISABLE_CDC_SQL)
        }
    }

    fun withAgentStarted() {
        return executeSqls("EXEC master.dbo.xp_servicecontrol N'START', N'SQLServerAGENT';")
    }

    fun withAgentStopped() {
        return executeSqls("EXEC master.dbo.xp_servicecontrol N'STOP', N'SQLServerAGENT';")
    }

    fun withWaitUntilAgentRunning() {
        waitForAgentState(true)
    }

    fun withWaitUntilAgentStopped() {
        waitForAgentState(false)
    }

    fun waitForCdcRecords(schemaName: String?, tableName: String?, recordCount: Int) {
        waitForCdcRecords(schemaName, tableName, "${schemaName}_$tableName", recordCount)
    }

    fun waitForCdcRecords(schemaName: String?, tableName: String?, cdcInstanceName: String, recordCount: Int) {
        if (!CDC_INSTANCE_NAMES.contains(cdcInstanceName)) {
            throw RuntimeException("CDC is not enabled on instance $cdcInstanceName")
        }
        val sql = "SELECT count(*) FROM cdc.${cdcInstanceName}_ct"
        var actualRecordCount = 0
        for (tryCount in 0 until MAX_RETRIES) {
            LOGGER.info(formatLogLine("fetching the number of CDC records for {}.{}, instance {}"), schemaName, tableName, cdcInstanceName)
            try {
                Thread.sleep(1000)
                actualRecordCount = executeQuery(sql, Int::class.java)[0][0] as Int
            } catch (e: SQLException) {
                actualRecordCount = 0
            } catch (e: Exception) {
                actualRecordCount = 0
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
            LOGGER.info(
                formatLogLine("Found {} CDC records for {}.{} in instance {}. Expecting {}. Trying again ({}/{}"), actualRecordCount, schemaName,
                tableName, cdcInstanceName,
                recordCount, tryCount, MAX_RETRIES
            )
            if (actualRecordCount >= recordCount) {
                LOGGER.info(formatLogLine("found {} records after {} tries!"), actualRecordCount, tryCount)
            }
        }
        throw RuntimeException(
            formatLogLine(
                "failed to find $recordCount records after $MAX_RETRIES seconds. Only found $actualRecordCount!"
            )
        )
    }

    private var shortenedPollingIntervalEnabled = false

    fun withShortenedCapturePollingInterval() {
        if (!shortenedPollingIntervalEnabled) {
            synchronized(container) {
                shortenedPollingIntervalEnabled = true
                executeSqls("EXEC sys.sp_cdc_change_job @job_type = 'capture', @pollinginterval = 1;")
            }
        }
    }

    private fun waitForAgentState(running: Boolean) {
        val expectedValue = if (running) "Running." else "Stopped."
        LOGGER.info(formatLogLine("Waiting for SQLServerAgent state to change to '{}'."), expectedValue)
        for (i in 0 until MAX_RETRIES) {
            try {
                Thread.sleep(1000)
                val r = executeQuery("EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';", String::class.java)[0]
                if (expectedValue.equals(r[0] as String, ignoreCase = true)) {
                    LOGGER.info(formatLogLine("SQLServerAgent state is '{}', as expected."), expectedValue)
                    return
                }
                LOGGER.info(formatLogLine("Retrying, SQLServerAgent state {} does not match expected '{}'."), r, expectedValue)
            } catch (e: SQLException) {
                LOGGER.info(formatLogLine("Retrying agent state query after catching exception {}."), e.message)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
        }
        throw RuntimeException(formatLogLine("Exhausted retry attempts while polling for agent state"))
    }

    fun withWaitUntilMaxLsnAvailable() {
        LOGGER.info(formatLogLine("Waiting for max LSN to become available for database {}."), databaseName)
        for (i in 0 until MAX_RETRIES) {
            try {
                Thread.sleep(1000)
                val maxLSN = executeQuery(MAX_LSN_QUERY, ByteArray::class.java)[0][0] as ByteArray?
                if (maxLSN != null) {
                    LOGGER.info(formatLogLine("Max LSN available for database {}: {}"), databaseName, Lsn.valueOf(maxLSN))
                }
                LOGGER.info(formatLogLine("Retrying, max LSN still not available for database {}."), databaseName)
            } catch (e: SQLException) {
                LOGGER.info(formatLogLine("Retrying max LSN query after catching exception {}"), e.message)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
        }
        throw RuntimeException("Exhausted retry attempts while polling for max LSN availability")
    }

    val password: String
        get() = "S00p3rS33kr3tP4ssw0rd!"

    val jdbcUrl: String
        get() = String.format("jdbc:sqlserver://%s:%d", container.host, container.firstMappedPort)

    override fun inContainerBootstrapCmd(): List<List<String>> {
        return listOf(
            mssqlCmd(listOf(String.format("CREATE DATABASE %s", databaseName))),
            mssqlCmd(
                listOf(
                    String.format("USE %s", databaseName),
                    String.format("CREATE LOGIN %s WITH PASSWORD = '%s', DEFAULT_DATABASE = %s", userName, password, databaseName),
                    String.format("ALTER SERVER ROLE [sysadmin] ADD MEMBER %s", userName),
                    String.format("CREATE USER %s FOR LOGIN %s WITH DEFAULT_SCHEMA = [dbo]", userName, userName),
                    String.format("ALTER ROLE [db_owner] ADD MEMBER %s", userName)
                )
            )
        )
    }

    /**
     * Don't drop anything when closing the test database. Instead, if cleanup is required, call
     * [.dropDatabaseAndUser] explicitly. Implicit cleanups may result in deadlocks and so
     * aren't really worth it.
     */
    override fun inContainerUndoBootstrapCmd(): List<String> {
        return emptyList<String>()
    }

    fun dropDatabaseAndUser() {
        execInContainer(
            *mssqlCmd(
                listOf(
                    String.format("USE master"),
                    String.format("ALTER DATABASE %s SET single_user WITH ROLLBACK IMMEDIATE", databaseName),
                    String.format("DROP DATABASE %s", databaseName)
                )
            ).toTypedArray()
        )
    }

    fun mssqlCmd(sql: List<String>): List<String> {
        return listOf(
            "/opt/mssql-tools18/bin/sqlcmd",
            "-U", container.username,
            "-P", container.password,
            "-Q", sql.joinToString("; "),
            "-b", "-e", "-C"
        )
    }

    enum class CertificateKey(@JvmField val isValid: Boolean) {
        CA(true),
        DUMMY_CA(false),
        SERVER(true),
        DUMMY_SERVER(false),
        SERVER_DUMMY_CA(false),
    }

    private val cachedCerts: MutableMap<CertificateKey, String> = ConcurrentHashMap()

    init {
        LOGGER.info("creating new database. databaseId=" + this.databaseId + ", databaseName=" + databaseName)
    }

    fun getCertificate(certificateKey: CertificateKey): String? {
        if (!cachedCerts.containsKey(certificateKey)) {
            val certificate: String
            try {
                val command = "cat /tmp/certs/" + certificateKey.name.lowercase(Locale.getDefault()) + ".crt"
                certificate = container.execInContainer("bash", "-c", command).stdout.trim { it <= ' ' }
            } catch (e: IOException) {
                throw UncheckedIOException(e)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
            synchronized(cachedCerts) {
                cachedCerts.put(certificateKey, certificate)
            }
        }
        return cachedCerts[certificateKey]
    }

    val schemaName = "schema_" + RandomStringUtils.insecure().nextAlphabetic(16)
    private var initialized = false

    override val config: MsSqlServerSourceConfigurationSpecification by lazy {
        config()
    }
    override val sourceConfigurationFactory = MsSqlServerSourceConfigurationFactory()


    protected fun config(): MsSqlServerSourceConfigurationSpecification {
        if (initialized) {
            throw RuntimeException("Already initialized!")
        }
        initialized = true
        val config =
            MsSqlServerSourceConfigurationSpecification().apply {
                host = container.host
                port =
                    container.getMappedPort(
                        MSSQLServerContainer.MS_SQL_SERVER_PORT
                    )
                username = container.username
                password = container.password
                jdbcUrlParams = ""
                database = databaseName
                schemas = arrayOf(schemaName)
                replicationMethodJson =
                    MsSqlServerCursorBasedReplicationConfigurationSpecification()
            }
        JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config.apply { database="master" })).get().use { connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("CREATE DATABASE $databaseName")
            }
        }
        JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config.apply { database=databaseName })).get().use { connection ->
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("CREATE SCHEMA $schemaName")
            }
            connection.createStatement().use { stmt: Statement ->
                stmt.execute(
                    "CREATE TABLE $schemaName.name_and_born(name VARCHAR(200), born DATETIMEOFFSET(7));"
                )
                stmt.execute(
                    "CREATE TABLE $schemaName.id_name_and_born(id INTEGER PRIMARY KEY, name VARCHAR(200), born DATETIMEOFFSET(7));"
                )
            }
            connection.createStatement().use { stmt: Statement ->
                stmt.execute(
                    "INSERT INTO $schemaName.name_and_born (name, born) VALUES ('foo', '2022-03-21 15:43:15.45'), ('bar', '2022-10-22 01:02:03.04')"
                )
                stmt.execute(
                    "INSERT INTO $schemaName.id_name_and_born (id, name, born) VALUES (1, 'foo', '2022-03-21 15:43:15.45'), (2, 'bar', '2022-10-22 01:02:03.04')"
                )
            }
        }
        return config
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(MsSQLTestDatabase::class.java)

        // Turning this to true will create a bunch of background threads that will regularly check the
        // state of the database and log every time it changes. A bit verbose, but useful for debugging
        private const val ENABLE_BACKGROUND_THREADS = false

        // empirically, 240 is enough. If you fee like you need to increase it, you're probably mmissing a
        // check somewhere
        const val MAX_RETRIES: Int = 240

        @JvmStatic
        fun `in`(image: MsSqlServerImage, vararg modifiers: MsSqlServerContainerFactory.MsSqlServerContainerModifier): MsSQLTestDatabase {
            val container: MsSqlServercontainer = MsSqlServerContainerFactory.shared(image, *modifiers)
            val testdb = MsSQLTestDatabase(container)
            return testdb.apply {
                addConnectionProperty("encrypt", "false")
                addConnectionProperty("trustServerCertificate", "true")
                addConnectionProperty("databaseName", testdb.databaseName)
                initialize()
            }
        }

        private const val RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT =
            "The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting. Try again later.'"
        private fun getEnableCdcSql(schemaName: String, tableName: String, roleName: String, instanceName: String): String = """
                                                   EXEC sys.sp_cdc_enable_table
                                                   ${'\t'}@source_schema = N'$schemaName',
                                                   ${'\t'}@source_name   = N'$tableName',
                                                   ${'\t'}@role_name     = $roleName,
                                                   ${'\t'}@supports_net_changes = 0,
                                                   ${'\t'}@capture_instance = N'$instanceName'
                                                   """.trimIndent()
        private fun getDisableCdcSql(schemaName: String, tableName: String, instanceName: String): String = """
                                                    EXEC sys.sp_cdc_disable_table
                                                    ${'\t'}@source_schema = N'$schemaName',
                                                    ${'\t'}@source_name   = N'$tableName',
                                                    ${'\t'}@capture_instance = N'$instanceName'
                                                    """.trimIndent()

        private const val DISABLE_CDC_SQL = "EXEC sys.sp_cdc_disable_db;"

        const val MAX_LSN_QUERY: String = "SELECT sys.fn_cdc_get_max_lsn();"
    }
}
