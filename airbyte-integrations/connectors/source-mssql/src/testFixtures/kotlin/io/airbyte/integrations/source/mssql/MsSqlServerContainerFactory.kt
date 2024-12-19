/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCdcReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCursorBasedReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.debezium.connector.sqlserver.Lsn
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.lang3.RandomStringUtils
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName
import java.sql.SQLException
import java.sql.Statement
import java.util.concurrent.atomic.AtomicInteger

private val log = KotlinLogging.logger {}
enum class MsSqlServerImage(val imageName: String) {
    SQLSERVER_2022("mcr.microsoft.com/mssql/server:2022-latest")
}

class MsSqlServercontainerWithCdc(realContainer: MSSQLServerContainer<*>): MsSqlServercontainer(realContainer) {
    override val config: MsSqlServerSourceConfigurationSpecification by lazy {
        cdcConfig()
    }

    private fun cdcConfig(): MsSqlServerSourceConfigurationSpecification {
        val configWithoutCdc = config()
        configureCdc(configWithoutCdc)
        val retVal = configWithoutCdc.apply {
            replicationMethodJson = MsSqlServerCdcReplicationConfigurationSpecification()
        }
        return retVal
    }
    private fun configureCdc(configWithoutCdc: MsSqlServerSourceConfigurationSpecification) {
        JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(configWithoutCdc)).get().use { connection ->
            connection.isReadOnly = false
            connection.createStatement().use {
                it.execute("EXEC sys.sp_cdc_enable_db")
            }
            waitForAgentState(configWithoutCdc, true)
            /*connection.createStatement().use {
                it.execute(ENABLE_CDC_SQL_FMT.format(schemaName, "name_and_born", "RANDOM_ROLE", "cdc_${schemaName}_name_and_born"))
            }*/
        }
    }
    fun withWaitUntilMaxLsnAvailable(config: MsSqlServerSourceConfigurationSpecification) {
        JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config)).get().use { connection ->
            connection.isReadOnly = false
            for (i in 0 until 50) {
                try {
                    Thread.sleep(1000)
                    val maxLsn: ByteArray?
                    connection.createStatement().use {
                        val rs = it.executeQuery("SELECT sys.fn_cdc_get_max_lsn();")
                        rs.next()
                        maxLsn = rs.getBytes(1)
                    }
                    if (maxLsn != null) {
                        log.info { "Max LSN available for database ${Lsn.valueOf(maxLsn)}" }
                        return
                    }
                    log.info { "Retrying, max LSN still not available for database." }
                } catch (e: SQLException) {
                    log.info { "Retrying max LSN query after catching exception ${e.message}" }
                }
            }
            throw RuntimeException("Exhausted retry attempts while polling for max LSN availability")
        }
    }

    private fun waitForAgentState(config: MsSqlServerSourceConfigurationSpecification, running: Boolean) {
        val expectedValue = if (running) "Running." else "Stopped."
        log.info{"Waiting for SQLServerAgent state to change to '$expectedValue'."}
        for (i in 0 until MAX_RETRIES) {
            try {
                val agentState: String?
                Thread.sleep(1000)
                JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config)).get().use { connection ->
                    connection.createStatement().use {
                        val rs = it.executeQuery("EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';")
                        rs.next()
                        agentState = rs.getString(1)
                    }
                }
                if (expectedValue.equals(agentState, ignoreCase = true)) {
                    log.info{"SQLServerAgent state is '$expectedValue', as expected."}
                    return
                }
                log.info{"Retrying, SQLServerAgent state $agentState does not match expected '$expectedValue'."}
            } catch (e: SQLException) {
                log.info{"Retrying agent state query after catching exception ${e.message}."}
            } catch (e: InterruptedException) {
                throw java.lang.RuntimeException(e)
            }
        }
        throw java.lang.RuntimeException("Exhausted retry attempts while polling for agent state")
    }

    companion object {
        private val RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT =
            "The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting. Try again later.'"
        val ENABLE_CDC_SQL_FMT = """
                                                  EXEC sys.sp_cdc_enable_table
                                                   ${'\t'}@source_schema = N'%s',
                                                   ${'\t'}@source_name   = N'%s',
                                                   ${'\t'}@role_name     = %s,
                                                   ${'\t'}@supports_net_changes = 0,
                                                   ${'\t'}@capture_instance = N'%s'
                                                   """.trimIndent()

        // empirically, 240 is enough. If you fee like you need to increase it, you're probably mmissing a
        // check somewhere
        val MAX_RETRIES: Int = 240

        val counter = AtomicInteger(0)
    }
}

open class MsSqlServercontainer(val realContainer: MSSQLServerContainer<*>): AutoCloseable {
    val id = counter.incrementAndGet()
    val schemaName = "schema_" + RandomStringUtils.insecure().nextAlphabetic(16)
    val databaseName = "db_" + RandomStringUtils.insecure().nextAlphabetic(16)
    private var initialized = false

    open val config: MsSqlServerSourceConfigurationSpecification by lazy {
        config()
    }


    protected fun config(): MsSqlServerSourceConfigurationSpecification {
        if (initialized) {
            throw RuntimeException("Already initialized!")
        }
        initialized = true
        val config =
            MsSqlServerSourceConfigurationSpecification().apply {
                host = realContainer.host
                port =
                    realContainer.getMappedPort(
                        MSSQLServerContainer.MS_SQL_SERVER_PORT
                    )
                username = realContainer.username
                password = realContainer.password
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
        val counter = AtomicInteger(0)
    }

    override fun close() {
        realContainer.close()
    }
}

object MsSqlServerContainerFactory {
    const val COMPATIBLE_NAME = "mcr.microsoft.com/mssql/server"

    init {
        TestContainerFactory.register(COMPATIBLE_NAME) { imageName: DockerImageName ->
            MSSQLServerContainer<Nothing>(imageName)
        }
    }

    sealed interface MsSqlServerContainerModifier :
        TestContainerFactory.ContainerModifier<MSSQLServerContainer<*>>

    data object WithNetwork : MsSqlServerContainerModifier {
        override fun modify(container: MSSQLServerContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }
    }

    data object WithCdcAgent : MsSqlServerContainerModifier {
        override fun modify(container: MSSQLServerContainer<*>) {
            container.addEnv("MSSQL_AGENT_ENABLED", "True");
        }
    }

    data object WithSslCertificates : MsSqlServerContainerModifier {
        override fun modify(container: MSSQLServerContainer<*>) {
            container.addEnv("MSSQL_AGENT_ENABLED", "True");
        }
    }

    private data object DefaultModifier: MsSqlServerContainerModifier {
        override fun modify(container: MSSQLServerContainer<*>) {
            container.addEnv("MSSQL_MEMORY_LIMIT_MB", "384")
        }

    }

    fun exclusive(
        image: MsSqlServerImage,
        vararg modifiers: MsSqlServerContainerModifier,
    ): MsSqlServercontainer {
        val dockerImageName =
            DockerImageName.parse(image.imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        val realContainer = TestContainerFactory.exclusive(dockerImageName, *modifiers)
        if (modifiers.contains(WithCdcAgent)) {
            return MsSqlServercontainerWithCdc(realContainer)
        } else {
            return MsSqlServercontainer(realContainer)
        }
    }

    fun shared(
        image: MsSqlServerImage,
        vararg modifiers: MsSqlServerContainerModifier,
    ): MsSqlServercontainer {
        val dockerImageName =
            DockerImageName.parse(image.imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return MsSqlServercontainer(TestContainerFactory.shared(dockerImageName, *modifiers))
    }
}
