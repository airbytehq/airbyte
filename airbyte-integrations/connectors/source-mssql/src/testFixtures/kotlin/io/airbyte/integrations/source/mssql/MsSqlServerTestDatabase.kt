/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql

import com.google.common.collect.Sets
import io.airbyte.cdk.test.fixtures.legacy.ContainerFactory
import io.airbyte.cdk.test.fixtures.legacy.DatabaseDriver
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.JDBC_URL_PARAMS_KEY
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.SCHEMAS_KEY
import io.airbyte.cdk.test.fixtures.legacy.TestDatabase
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.MsSQLConfigBuilder
import io.debezium.connector.sqlserver.Lsn
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.jooq.exception.DataAccessException
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.testcontainers.containers.MSSQLServerContainer
import java.io.IOException
import java.io.UncheckedIOException
import java.sql.SQLException
import java.util.*
import java.util.concurrent.ConcurrentHashMap
import java.util.function.Consumer
import java.util.stream.Collectors
import java.util.stream.Stream
import kotlin.collections.MutableMap
import kotlin.collections.MutableSet

open class MsSQLTestDatabase(container: MSSQLServerContainer<*>) :
    TestDatabase<MSSQLServerContainer<*>, MsSQLTestDatabase, MsSQLConfigBuilder>(container) {
    enum class BaseImage(@JvmField val reference: String) {
        MSSQL_2022("mcr.microsoft.com/mssql/server:2022-latest"),
    }

    enum class ContainerModifier(override val modifier: Consumer<MSSQLServerContainer<*>>) :
        ContainerFactory.NamedContainerModifier<MSSQLServerContainer<*>> {
        AGENT(Consumer<MSSQLServerContainer<*>> { container: MSSQLServerContainer<*> -> MsSQLContainerFactory.withAgent(container) }),
        WITH_SSL_CERTIFICATES(Consumer<MSSQLServerContainer<*>> { container: MSSQLServerContainer<*> ->
            MsSQLContainerFactory.withSslCertificates(
                container
            )
        }),
        ;
    }

    fun withCdc(): MsSQLTestDatabase {
        LOGGER.info("enabling CDC on database {} with id {}", databaseName, databaseId)
        with("EXEC sys.sp_cdc_enable_db;")
        LOGGER.info("CDC enabled on database {} with id {}", databaseName, databaseId)
        return this
    }

    private val CDC_INSTANCE_NAMES: MutableSet<String> = Sets.newConcurrentHashSet()

    fun withCdcForTable(schemaName: String?, tableName: String?, roleName: String?): MsSQLTestDatabase {
        return withCdcForTable(schemaName, tableName, roleName, "${schemaName}_$tableName")
    }

    open fun withCdcForTable(schemaName: String?, tableName: String?, roleName: String?, instanceName: String): MsSQLTestDatabase {
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
                    with(getEnableCdcSql(schemaName, tableName, sqlRoleName, instanceName))
                }
                CDC_INSTANCE_NAMES.add(instanceName)
                return withShortenedCapturePollingInterval()
            } catch (e: DataAccessException) {
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

    open fun withCdcDisabledForTable(schemaName: String?, tableName: String?, instanceName: String): MsSQLTestDatabase? {
        LOGGER.info(formatLogLine("disabling CDC for table {}.{}, instance {}"), schemaName, tableName, instanceName)
        if (!CDC_INSTANCE_NAMES.remove(instanceName)) {
            throw RuntimeException(formatLogLine("CDC was disabled for instance ") + instanceName)
        }
        synchronized(container) {
            return with(getEnableCdcSql(schemaName, tableName, instanceName))
        }
    }

    fun withoutCdc(): MsSQLTestDatabase? {
        CDC_INSTANCE_NAMES.clear()
        synchronized(container) {
            return with(DISABLE_CDC_SQL)
        }
    }

    fun withAgentStarted(): MsSQLTestDatabase? {
        return with("EXEC master.dbo.xp_servicecontrol N'START', N'SQLServerAGENT';")
    }

    fun withAgentStopped(): MsSQLTestDatabase? {
        return with("EXEC master.dbo.xp_servicecontrol N'STOP', N'SQLServerAGENT';")
    }

    fun withWaitUntilAgentRunning(): MsSQLTestDatabase {
        waitForAgentState(true)
        return self()
    }

    fun withWaitUntilAgentStopped(): MsSQLTestDatabase? {
        waitForAgentState(false)
        return self()
    }

    fun waitForCdcRecords(schemaName: String?, tableName: String?, recordCount: Int): MsSQLTestDatabase? {
        return waitForCdcRecords(schemaName, tableName, "${schemaName}_$tableName", recordCount)
    }

    fun waitForCdcRecords(schemaName: String?, tableName: String?, cdcInstanceName: String, recordCount: Int): MsSQLTestDatabase? {
        if (!CDC_INSTANCE_NAMES.contains(cdcInstanceName)) {
            throw RuntimeException("CDC is not enabled on instance $cdcInstanceName")
        }
        val sql = "SELECT count(*) FROM cdc.${cdcInstanceName}_ct"
        var actualRecordCount = 0
        for (tryCount in 0 until MAX_RETRIES) {
            LOGGER.info(formatLogLine("fetching the number of CDC records for {}.{}, instance {}"), schemaName, tableName, cdcInstanceName)
            try {
                Thread.sleep(1000)
                actualRecordCount = query { ctx: DSLContext -> ctx.fetch(sql) }!![0].get(0, Int::class.java)
            } catch (e: SQLException) {
                actualRecordCount = 0
            } catch (e: DataAccessException) {
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
                return self()
            }
        }
        throw RuntimeException(
            formatLogLine(
                "failed to find $recordCount records after $MAX_RETRIES seconds. Only found $actualRecordCount!"
            )
        )
    }

    private var shortenedPollingIntervalEnabled = false

    fun withShortenedCapturePollingInterval(): MsSQLTestDatabase {
        if (!shortenedPollingIntervalEnabled) {
            synchronized(container) {
                shortenedPollingIntervalEnabled = true
                with("EXEC sys.sp_cdc_change_job @job_type = 'capture', @pollinginterval = 1;")
            }
        }
        return this
    }

    private fun waitForAgentState(running: Boolean) {
        val expectedValue = if (running) "Running." else "Stopped."
        LOGGER.info(formatLogLine("Waiting for SQLServerAgent state to change to '{}'."), expectedValue)
        for (i in 0 until MAX_RETRIES) {
            try {
                Thread.sleep(1000)
                val r = query { ctx: DSLContext -> ctx.fetch("EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';")[0] }
                if (expectedValue.equals(r!!.getValue(0).toString(), ignoreCase = true)) {
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

    fun withWaitUntilMaxLsnAvailable(): MsSQLTestDatabase? {
        LOGGER.info(formatLogLine("Waiting for max LSN to become available for database {}."), databaseName)
        for (i in 0 until MAX_RETRIES) {
            try {
                Thread.sleep(1000)
                val maxLSN = query { ctx: DSLContext -> ctx.fetch(MAX_LSN_QUERY)[0].get(0, ByteArray::class.java) }
                if (maxLSN != null) {
                    LOGGER.info(formatLogLine("Max LSN available for database {}: {}"), databaseName, Lsn.valueOf(maxLSN))
                    return self()
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

    override val password: String
        get() = "S00p3rS33kr3tP4ssw0rd!"

    override val jdbcUrl: String
        get() = String.format("jdbc:sqlserver://%s:%d", container.host, container.firstMappedPort)

    override fun inContainerBootstrapCmd(): Stream<Stream<String>> {
        return Stream.of(
            mssqlCmd(Stream.of(String.format("CREATE DATABASE %s", databaseName))),
            mssqlCmd(
                Stream.of(
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
    override fun inContainerUndoBootstrapCmd(): Stream<String> {
        return Stream.empty()
    }

    fun dropDatabaseAndUser() {
        execInContainer(
            mssqlCmd(
                Stream.of(
                    String.format("USE master"),
                    String.format("ALTER DATABASE %s SET single_user WITH ROLLBACK IMMEDIATE", databaseName),
                    String.format("DROP DATABASE %s", databaseName)
                )
            )
        )
    }

    fun mssqlCmd(sql: Stream<String>): Stream<String> {
        return Stream.of(
            "/opt/mssql-tools18/bin/sqlcmd",
            "-U", container.username,
            "-P", container.password,
            "-Q", sql.collect(Collectors.joining("; ")),
            "-b", "-e", "-C"
        )
    }

    override val databaseDriver: DatabaseDriver
        get() = DatabaseDriver.MSSQLSERVER

    override val sqlDialect: SQLDialect
        get() = SQLDialect.DEFAULT

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

    override fun configBuilder(): MsSQLConfigBuilder {
        return MsSQLConfigBuilder(this)
    }

    class MsSQLConfigBuilder(testDatabase: MsSQLTestDatabase) : ConfigBuilder<MsSQLTestDatabase, MsSQLConfigBuilder>(testDatabase) {
        init {
            with(JDBC_URL_PARAMS_KEY, "loginTimeout=2")
        }

        fun withCdcReplication(): MsSQLConfigBuilder {
            return with("is_test", true)
                .with(
                    "replication_method", mapOf(
                        "method" to "CDC",
                        "initial_waiting_seconds" to DEFAULT_CDC_REPLICATION_INITIAL_WAIT.seconds,
                        MsSqlSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY to MsSqlSpecConstants.RESYNC_DATA_OPTION
                    )
                )
        }

        fun withSchemas(vararg schemas: String?): MsSQLConfigBuilder {
            return with(SCHEMAS_KEY, listOf<String?>(*schemas))
        }

        override fun withoutSsl(): MsSQLConfigBuilder {
            return withSsl(mutableMapOf("ssl_method" to "unencrypted"))
        }

        override fun withSsl(sslMode: MutableMap<Any?, Any?>): MsSQLConfigBuilder {
            return with("ssl_method", sslMode)
        }

        fun withEncrytedTrustServerCertificate(): MsSQLConfigBuilder {
            return withSsl(mutableMapOf("ssl_method" to "encrypted_trust_server_certificate"))
        }

        fun withEncrytedVerifyServerCertificate(certificate: String?, hostnameInCertificate: String?): MsSQLConfigBuilder? {
            return if (hostnameInCertificate != null) {
                withSsl(
                    mutableMapOf(
                        "ssl_method" to "encrypted_verify_certificate",
                        "certificate" to certificate,
                        "hostNameInCertificate" to hostnameInCertificate
                    )
                )
            } else {
                withSsl(
                    mutableMapOf(
                        "ssl_method" to "encrypted_verify_certificate",
                        "certificate" to certificate
                    )
                )
            }
        }
    }

    override fun close() {
        //MssqlDebeziumStateUtil.disposeInitialState()
        super.close()
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
        fun `in`(imageName: BaseImage, vararg modifiers: ContainerModifier): MsSQLTestDatabase {
            val container: MSSQLServerContainer<out MSSQLServerContainer<*>> = MsSQLContainerFactory().shared(imageName.reference, *modifiers)
            val testdb =
                MsSQLTestDatabase(container)
            return testdb
                .withConnectionProperty("encrypt", "false")
                .withConnectionProperty("trustServerCertificate", "true")
                .withConnectionProperty("databaseName", testdb.databaseName)
                .initialized()
        }

        private const val RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT =
            "The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting. Try again later.'"
        private fun getEnableCdcSql(schemaName: String?, tableName: String?, sqlRoleName: String, instanceName: String): String = """
                                                   EXEC sys.sp_cdc_enable_table
                                                   ${'\t'}@source_schema = N'$schemaName',
                                                   ${'\t'}@source_name   = N'$tableName',
                                                   ${'\t'}@role_name     = $sqlRoleName,
                                                   ${'\t'}@supports_net_changes = 0,
                                                   ${'\t'}@capture_instance = N'$instanceName'
                                                   """.trimIndent()
        private fun getEnableCdcSql(schemaName: String?, tableName: String?, instanceName: String): String = """
                                                    EXEC sys.sp_cdc_disable_table
                                                    ${'\t'}@source_schema = N'$schemaName',
                                                    ${'\t'}@source_name   = N'$tableName',
                                                    ${'\t'}@capture_instance = N'$instanceName'
                                                    """.trimIndent()

        private const val DISABLE_CDC_SQL = "EXEC sys.sp_cdc_disable_db;"

        const val MAX_LSN_QUERY: String = "SELECT sys.fn_cdc_get_max_lsn();"
    }
}
