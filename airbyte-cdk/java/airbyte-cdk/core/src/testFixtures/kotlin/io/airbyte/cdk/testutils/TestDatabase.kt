/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.testutils

import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.ContextQueryFunction
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.DSLContextFactory
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.JdbcConnector
import io.airbyte.cdk.integrations.util.HostPortResolver
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.UncheckedIOException
import java.sql.SQLException
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.time.Duration
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import java.util.stream.Stream
import javax.sql.DataSource
import kotlin.concurrent.Volatile
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.testcontainers.containers.JdbcDatabaseContainer

private val LOGGER = KotlinLogging.logger {}
/**
 * TestDatabase provides a convenient pattern for interacting with databases when testing SQL
 * database sources. The basic idea is to share the same database testcontainer instance for all
 * tests and to use SQL constructs such as DATABASE and USER to isolate each test case's state.
 *
 * @param <C> the type of the backing testcontainer.
 * @param <T> itself
 * @param <B> the type of the object returned by [.configBuilder] </B></T></C>
 */
abstract class TestDatabase<
    C : JdbcDatabaseContainer<*>, T : TestDatabase<C, T, B>, B : TestDatabase.ConfigBuilder<T, B>>
protected constructor(val container: C) : AutoCloseable {
    private val suffix: String = Strings.addRandomSuffix("", "_", 10)
    private val cleanupSQL: ArrayList<String> = ArrayList()
    private val connectionProperties: MutableMap<String, String> = HashMap()

    @Volatile private var dataSource: DataSource? = null

    @Volatile private lateinit var dslContext: DSLContext

    @JvmField protected val databaseId: Int = nextDatabaseId.getAndIncrement()
    @JvmField
    protected val containerId: Int =
        containerUidToId.computeIfAbsent(container.containerId) { _: String ->
            nextContainerId.getAndIncrement()
        }
    private val dateFormat: DateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS")

    init {
        LOGGER!!.info(formatLogLine("creating database $databaseName"))
    }

    protected fun formatLogLine(logLine: String?): String {
        val retVal = "TestDatabase databaseId=$databaseId, containerId=$containerId - $logLine"
        return retVal
    }

    @Suppress("UNCHECKED_CAST")
    protected fun self(): T {
        return this as T
    }

    /** Adds a key-value pair to the JDBC URL's query parameters. */
    fun withConnectionProperty(key: String, value: String): T {
        if (this.isInitialized) {
            throw RuntimeException("TestDatabase instance is already initialized")
        }
        connectionProperties[key] = value
        return self()
    }

    /** Enqueues a SQL statement to be executed when this object is closed. */
    fun onClose(fmtSql: String, vararg fmtArgs: Any?): T {
        cleanupSQL.add(String.format(fmtSql, *fmtArgs))
        return self()
    }

    /** Executes a SQL statement after calling String.format on the arguments. */
    fun with(fmtSql: String, vararg fmtArgs: Any?): T {
        execSQL(Stream.of(String.format(fmtSql, *fmtArgs)))
        return self()
    }

    /**
     * Executes SQL statements as root to provide the necessary isolation for the lifetime of this
     * object. This typically entails at least a CREATE DATABASE and a CREATE USER. Also Initializes
     * the [DataSource] and [DSLContext] owned by this object.
     */
    open fun initialized(): T {
        inContainerBootstrapCmd().forEach { cmds: Stream<String> -> this.execInContainer(cmds) }
        this.dataSource =
            DataSourceFactory.create(
                userName,
                password,
                databaseDriver!!.driverClassName,
                jdbcUrl,
                connectionProperties.toMap(),
                JdbcConnector.getConnectionTimeout(
                    connectionProperties.toMap(),
                    databaseDriver!!.driverClassName
                )
            )
        this.dslContext = DSLContextFactory.create(dataSource, sqlDialect)
        return self()
    }

    val isInitialized: Boolean
        get() = ::dslContext.isInitialized

    protected abstract fun inContainerBootstrapCmd(): Stream<Stream<String>>

    protected abstract fun inContainerUndoBootstrapCmd(): Stream<String>

    abstract val databaseDriver: DatabaseDriver?

    abstract val sqlDialect: SQLDialect?

    fun withNamespace(name: String?): String {
        return name + suffix
    }

    open val databaseName: String
        get() = withNamespace("db")

    val userName: String
        get() = withNamespace("user")

    open val password: String?
        get() = "password"

    fun getDataSource(): DataSource? {
        if (!this.isInitialized) {
            throw RuntimeException("TestDatabase instance is not yet initialized")
        }
        return dataSource
    }

    fun getDslContext(): DSLContext {
        if (!this.isInitialized) {
            throw RuntimeException("TestDatabase instance is not yet initialized")
        }
        return dslContext
    }

    open val jdbcUrl: String?
        get() =
            String.format(
                databaseDriver!!.urlFormatString,
                container.host,
                container.firstMappedPort,
                databaseName
            )

    val database: Database
        get() = Database(getDslContext())

    protected fun execSQL(sql: Stream<String>) {
        try {
            database.query<Any?> { ctx: DSLContext ->
                sql.forEach { statement: String ->
                    LOGGER!!.info("executing SQL statement {}", statement)
                    ctx.execute(statement)
                }
                null
            }
        } catch (e: SQLException) {
            throw RuntimeException(e)
        }
    }

    protected fun execInContainer(cmds: Stream<String>) {
        val cmd = cmds.toList()
        if (cmd.isEmpty()) {
            return
        }
        try {
            LOGGER!!.info(
                formatLogLine(
                    String.format("executing command %s", Strings.join(cmd.asIterable(), " "))
                )
            )
            val exec = container.execInContainer(*cmd.toTypedArray<String>())
            if (exec!!.exitCode == 0) {
                LOGGER.info(
                    formatLogLine(
                        String.format(
                            "execution success\nstdout:\n%s\nstderr:\n%s",
                            exec.stdout,
                            exec.stderr
                        )
                    )
                )
            } else {
                LOGGER.error(
                    formatLogLine(
                        String.format(
                            "execution failure, code %s\nstdout:\n%s\nstderr:\n%s",
                            exec.exitCode,
                            exec.stdout,
                            exec.stderr
                        )
                    )
                )
            }
        } catch (e: IOException) {
            throw UncheckedIOException(e)
        } catch (e: InterruptedException) {
            throw RuntimeException(e)
        }
    }

    @Throws(SQLException::class)
    fun <X> query(transform: ContextQueryFunction<X>): X? {
        return database.query(transform)
    }

    @Throws(SQLException::class)
    fun <X> transaction(transform: ContextQueryFunction<X>): X? {
        return database.transaction(transform)
    }

    /** Returns a builder for the connector config object. */
    open fun configBuilder(): B {
        return ConfigBuilder<T, B>(self()).self()
    }

    fun testConfigBuilder(): B {
        return configBuilder().withHostAndPort().withCredentials().withDatabase()
    }

    fun integrationTestConfigBuilder(): B {
        return configBuilder().withResolvedHostAndPort().withCredentials().withDatabase()
    }

    override fun close() {
        execSQL(cleanupSQL.stream())
        execInContainer(inContainerUndoBootstrapCmd())
        LOGGER!!.info("closing database databaseId=$databaseId")
    }

    open class ConfigBuilder<T : TestDatabase<*, *, *>, B : ConfigBuilder<T, B>>(
        protected val testDatabase: T
    ) {
        protected val builder: ImmutableMap.Builder<Any, Any> = ImmutableMap.builder()

        fun build(): ObjectNode {
            return Jsons.jsonNode(builder.build()) as ObjectNode
        }

        @Suppress("UNCHECKED_CAST")
        fun self(): B {
            return this as B
        }

        fun with(key: Any, value: Any): B {
            builder.put(key, value)
            return self()
        }

        fun withDatabase(): B {
            return this.with(JdbcUtils.DATABASE_KEY, testDatabase.databaseName)
        }

        fun withCredentials(): B {
            return this.with(JdbcUtils.USERNAME_KEY, testDatabase.userName)
                .with(JdbcUtils.PASSWORD_KEY, testDatabase.password!!)
        }

        fun withResolvedHostAndPort(): B {
            return this.with(
                    JdbcUtils.HOST_KEY,
                    HostPortResolver.resolveHost(testDatabase.container)
                )
                .with(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(testDatabase.container))
        }

        fun withHostAndPort(): B {
            return this.with(JdbcUtils.HOST_KEY, testDatabase.container.host)
                .with(JdbcUtils.PORT_KEY, testDatabase.container.firstMappedPort)
        }

        open fun withoutSsl(): B {
            return with(JdbcUtils.SSL_KEY, false)
        }

        open fun withSsl(sslMode: MutableMap<Any?, Any?>): B {
            return with(JdbcUtils.SSL_KEY, true).with(JdbcUtils.SSL_MODE_KEY, sslMode)
        }

        companion object {
            @JvmField val DEFAULT_CDC_REPLICATION_INITIAL_WAIT: Duration = Duration.ofSeconds(5)
        }
    }

    companion object {

        private val nextDatabaseId: AtomicInteger = AtomicInteger(0)

        private val nextContainerId: AtomicInteger = AtomicInteger(0)
        private val containerUidToId: MutableMap<String, Int> = ConcurrentHashMap()
    }
}
