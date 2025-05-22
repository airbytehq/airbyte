// Copyright (c) 2024 Airbyte, Inc., all rights reserved.

package io.airbyte.integrations.source.tests

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.DriverManager
import java.sql.SQLException
import java.util.Properties
import org.testcontainers.containers.JdbcDatabaseContainer

interface TestDbInstance {
    fun connect()

    fun disconnect()

    fun getHost(): String

    fun getPort(): Int

    fun getUsername(): String

    fun getPassword(): String

    fun executeReadQuery(query: String): QueryResult

    fun executeUpdate(query: String)
}

/** Result class for read query operations */
data class QueryResult(
    val rows: List<Map<String, Any?>>,
    val columnNames: List<String>,
    val rowCount: Int,
)

/**
 * Abstract JDBC implementation for test databases. This follows the Template Method pattern and
 * handles all JDBC communication.
 */
abstract class AbstractJdbcTestDbInstance : TestDbInstance {

    private val log = KotlinLogging.logger {}

    protected var connection: Connection? = null

    protected abstract fun getJdbcUrl(): String

    protected abstract fun getProperties(): Properties

    protected fun isConnected(): Boolean = connection?.isClosed == false

    override fun executeReadQuery(query: String): QueryResult {
        requireConnection()

        val statement = connection!!.createStatement()
        log.info { "Executing read query: $query" }
        val resultSet = statement.executeQuery(query)
        val metaData = resultSet.metaData
        val columnCount = metaData.columnCount

        val columnNames = (1..columnCount).map { metaData.getColumnName(it) }
        val rows: MutableList<Map<String, Any?>> = mutableListOf()

        while (resultSet.next()) {
            val row = mutableMapOf<String, Any?>()
            for (i in 1..columnCount) {
                row[metaData.getColumnName(i)] = resultSet.getObject(i)
            }
            rows.add(row)
        }

        resultSet.close()
        statement.close()

        return QueryResult(rows, columnNames, rows.size)
    }

    override fun executeUpdate(query: String) {
        requireConnection()

        val statement = connection!!.createStatement()
        log.info { "Executing update query: $query" }
        statement.executeUpdate(query)
        statement.close()
    }

    override fun connect() {
        if (isConnected()) return

        connection = DriverManager.getConnection(getJdbcUrl(), getProperties())
    }

    override fun disconnect() {
        if (!isConnected()) return

        try {
            connection?.close()
            connection = null
        } catch (e: SQLException) {
            println("Failed to disconnect from database: ${e.message}")
        }
    }

    private fun requireConnection() {
        if (!isConnected()) {
            throw IllegalStateException("Database connection is not established")
        }
    }
}

/** Implementation for connecting to a remote database via JDBC */
class RemoteJdbcTestInstance(
    private val jdbcUrlPrefix: String,
    private val host: String,
    private val port: Int,
    private val username: String,
    private val password: String,
) : AbstractJdbcTestDbInstance() {
    override fun getJdbcUrl(): String = "$jdbcUrlPrefix://$host:$port"

    override fun getHost(): String = host

    override fun getPort(): Int = port

    override fun getUsername(): String = username

    override fun getPassword(): String = password

    override fun getProperties(): Properties =
        Properties().apply {
            put("user", username)
            put("password", password)
        }
}

/** Implementation that uses TestContainers to create and manage the database */
class ContainerizedDbInstance<T : JdbcDatabaseContainer<*>>(
    private val container: T,
    private val config: JdbcSourceConfiguration,
) : AbstractJdbcTestDbInstance() {
    override fun getJdbcUrl(): String = container.jdbcUrl

    override fun getHost(): String = container.host

    override fun getPort(): Int = container.firstMappedPort

    override fun getUsername(): String = container.username

    override fun getPassword(): String = container.password

    override fun getProperties(): Properties = Properties().apply { putAll(config.jdbcProperties) }

    override fun connect() {
        if (isConnected()) return

        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        connection = jdbcConnectionFactory.get()
    }
}
