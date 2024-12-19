package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.*
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.lang3.RandomStringUtils
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
import org.testcontainers.containers.JdbcDatabaseContainer
import java.sql.Connection
import java.sql.Statement

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
abstract class TestDatabase<C_SPEC: ConfigurationSpecification, SC: JdbcSourceConfiguration>
protected constructor(protected val container: JdbcDatabaseContainer<*>) : AutoCloseable {
    private val suffix: String = "_" + RandomStringUtils.insecure().nextAlphanumeric(10)
    private val cleanupSQL: ArrayList<String> = ArrayList()
    abstract val config: C_SPEC
    abstract val sourceConfigurationFactory: SourceConfigurationFactory<C_SPEC, SC>
    private val connectionProperties: MutableMap<String, String> = HashMap()

    @JvmField protected val databaseId: Int = nextDatabaseId.getAndIncrement()
    @JvmField
    protected val containerId: Int =
        containerUidToId.computeIfAbsent(container.containerId) { _: String ->
            nextContainerId.getAndIncrement()
        }
    private val dateFormat: DateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS")

    init {
        LOGGER.info{formatLogLine("creating database $databaseName")}
    }

    protected fun formatLogLine(logLine: String?): String {
        val retVal = "TestDatabase databaseId=$databaseId, containerId=$containerId - $logLine"
        return retVal
    }

    /** Adds a key-value pair to the JDBC URL's query parameters. */
    fun addConnectionProperty(key: String, value: String){
        /*if (this.isInitialized) {
            throw RuntimeException("TestDatabase instance is already initialized")
        }*/
        connectionProperties[key] = value
    }

    /** Enqueues a SQL statement to be executed when this object is closed. */
    fun addCloseSql(fmtSql: String, vararg fmtArgs: Any?){
        cleanupSQL.add(String.format(fmtSql, *fmtArgs))
    }

    /**
     * Executes SQL statements as root to provide the necessary isolation for the lifetime of this
     * object. This typically entails at least a CREATE DATABASE and a CREATE USER. Also Initializes
     * the [DataSource] and [DSLContext] owned by this object.
     */
    open fun initialize(){
        inContainerBootstrapCmd().forEach { cmds: List<String> -> this.execInContainer(*cmds.toTypedArray()) }
    }

    protected abstract fun inContainerBootstrapCmd(): List<List<String>>

    protected abstract fun inContainerUndoBootstrapCmd(): List<String>

    open val databaseName: String = "db$suffix"
    open val userName: String = "user$suffix"

    private fun createConnection(): Connection {
        val retVal: Connection = JdbcConnectionFactory(sourceConfigurationFactory.make(config)).get()
        retVal.isReadOnly = false
        return retVal
    }

    protected fun executeSqls(vararg sqls: String) {
        val conn = createConnection()
        for (sql in sqls) {
            conn.createStatement().use { stmt: Statement ->
                stmt.execute(sql)
            }
        }
    }

    protected fun executeQuery(sql: String, vararg columnTypes: Class<*>): List<List<Any>> {
        val conn = createConnection()
        val retVal: MutableList<List<Any>> = ArrayList()
        conn.createStatement().use { stmt: Statement ->
            val rs = stmt.executeQuery(sql)
            while (rs.next()) {
                for (i in columnTypes.indices) {
                    val row: MutableList<Any> = ArrayList()
                    row.add(
                        rs.getObject(0, columnTypes[0])
                    )
                    retVal.add(row.toList())
                }
            }
        }
        return retVal.toList()
    }

    protected fun execInContainer(vararg cmds: String) {
        val cmd = cmds.toList()
        if (cmd.isEmpty()) {
            return
        }
        try {
            LOGGER.info {
                formatLogLine(
                    String.format("executing command %s", cmds.joinToString(" "))
                )
            }
            val exec = container.execInContainer(*cmd.toTypedArray<String>())
            if (exec!!.exitCode == 0) {
                LOGGER.info {
                    formatLogLine(
                        String.format(
                            "execution success\nstdout:\n%s\nstderr:\n%s",
                            exec.stdout,
                            exec.stderr
                        )
                    )
                }
            } else {
                LOGGER.error {
                    formatLogLine(
                        String.format(
                            "execution failure, code %s\nstdout:\n%s\nstderr:\n%s",
                            exec.exitCode,
                            exec.stdout,
                            exec.stderr
                        )
                    )
                }
            }
        } catch (e: IOException) {
            throw UncheckedIOException(e)
        } catch (e: InterruptedException) {
            throw RuntimeException(e)
        }
    }


    override fun close() {
        executeSqls(*cleanupSQL.toTypedArray())
        execInContainer(*inContainerUndoBootstrapCmd().toTypedArray())
        LOGGER.info{"closing database databaseId=$databaseId"}
    }

    companion object {

        private val nextDatabaseId: AtomicInteger = AtomicInteger(0)

        private val nextContainerId: AtomicInteger = AtomicInteger(0)
        private val containerUidToId: MutableMap<String, Int> = ConcurrentHashMap()
    }
}
