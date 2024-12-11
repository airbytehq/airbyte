/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCdcReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerCursorBasedReplicationConfigurationSpecification
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.lang3.RandomStringUtils
import org.testcontainers.containers.Container
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName
import java.sql.Statement
import java.util.concurrent.atomic.AtomicInteger

private val log = KotlinLogging.logger {}
enum class MsSqlServerImage(val imageName: String) {
    SQLSERVER_2022("mcr.microsoft.com/mssql/server:2022-latest")
}

class MsSqlServercontainer(val realContainer: MSSQLServerContainer<*>) {
    val id = counter.incrementAndGet()
    init {
        println("SGX creating container $id")
    }
    val schemaName = "schema_" + RandomStringUtils.insecure().nextAlphabetic(16)
    val databaseName = "db_" + RandomStringUtils.insecure().nextAlphabetic(16)
    private var initialized = false

    val config: MsSqlServerSourceConfigurationSpecification by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        config()
    }

    val cdcConfig: MsSqlServerSourceConfigurationSpecification by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        cdcConfig()
    }

    private fun cdcConfig(): MsSqlServerSourceConfigurationSpecification {
        println("SGX configuring container $id with CDC!")
        val configWithoutCdc = config()
        JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(configWithoutCdc)).get().use { connection ->
            connection.isReadOnly = false
            connection.createStatement().use {
                it.execute("EXEC sys.sp_cdc_enable_db;")
            }
            connection.createStatement().use {
                it.execute(ENABLE_CDC_SQL_FMT.format(schemaName, "name_and_born", "RANDOM_ROLE", "cdc_${schemaName}_name_and_born"))
            }
        }
        val retVal = configWithoutCdc.apply {
            replicationMethodJson = MsSqlServerCdcReplicationConfigurationSpecification()
        }
        println("SGX finishing initializing container $id with CDC!")
        return retVal
    }

    private fun config(): MsSqlServerSourceConfigurationSpecification {
        println("SGX configuring container $id without CDC! ${Thread.currentThread().stackTrace.toList()}")
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
        println("SGX finishing initializing container $id without CDC!")
        return config
    }

    companion object {
        private val RETRYABLE_CDC_TABLE_ENABLEMENT_ERROR_CONTENT =
            "The error returned was 14258: 'Cannot perform this operation while SQLServerAgent is starting. Try again later.'"
        private val ENABLE_CDC_SQL_FMT = """
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
        return MsSqlServercontainer(TestContainerFactory.exclusive(dockerImageName, *modifiers))
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
