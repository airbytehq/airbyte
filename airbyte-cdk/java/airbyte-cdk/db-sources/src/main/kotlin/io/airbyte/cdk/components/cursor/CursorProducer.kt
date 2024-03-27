package io.airbyte.cdk.components.cursor

import io.airbyte.cdk.components.ConsumerComponent
import io.airbyte.cdk.components.ProducerComponent
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.io.Serializable
import java.sql.Connection
import java.sql.DriverManager
import java.sql.ResultSet
import java.util.Properties
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

class CursorProducer
private constructor(
    val jdbcDriver: Class<*>,
    val jdbcUrl: String,
    val jdbcProperties: Properties,
    val stream: AirbyteStreamNameNamespacePair,
    val cursorColNames: List<String>,
    val dataColNames: List<String>,
    val limitSql: String,
    val resultSetAccessor: ResultSetAccessor,
    internal val consumer: ConsumerComponent<List<Any?>,*>,
    private val notifyStop: () -> Unit,
    internal val initialState: CursorState
) : ProducerComponent<CursorState> {

    internal val isClosed = AtomicBoolean()
    internal val finalState = AtomicReference(initialState)

    internal val whereClauseParameters: List<Serializable> =
        initialState.initialValues.flatMapIndexed { i, _ -> initialState.initialValues.take(i+1) }

    internal val sql: String = """
        SELECT ${listOf(cursorColNames, dataColNames).flatten().joinToString()}
        FROM ${listOfNotNull(stream.namespace, stream.name).joinToString(".")}
        WHERE ${
        if (initialState.initialValues.isEmpty()) {
            "1 = 1"
        } else {
            cursorColNames
                .mapIndexed { i, v -> cursorColNames.take(i).map { "$it = ?" } + "$v > ?" }
                .map { it.joinToString(" AND ", "(", ")") }
                .joinToString(" OR ")
        }
        }
        ORDER BY ${cursorColNames.joinToString()}
        LIMIT ?
    """.trimIndent()

    override fun close() {
        isClosed.set(true)
    }

    override fun finalState(): CursorState = finalState.get()

    override fun run() {
        if (initialState.progress == CursorState.Progress.DONE) {
            return
        }
        jdbcDriver.getConstructor().newInstance()
        val conn: Connection = DriverManager.getConnection(jdbcUrl, jdbcProperties)
        conn.beginRequest()
        conn.isReadOnly = true
        val limit: Int = computeLimit(conn)
        val stmt = conn.prepareStatement(sql)
        whereClauseParameters.forEachIndexed { i, v -> stmt.setObject(i+1, v)}
        stmt.setInt(whereClauseParameters.size+1, limit)
        val resultSet: ResultSet = stmt.executeQuery()
        var rowCount = 0
        var currentRow: List<Any?> = listOf()
        while (!isClosed.get() && resultSet.next()) {
            currentRow = List(cursorColNames.size + dataColNames.size) { i ->
                val obj: Any? = resultSetAccessor.getColumnValue(resultSet, i+1)
                if (resultSet.wasNull()) null else obj
            }
            rowCount++
            consumer.accept(currentRow.drop(cursorColNames.size))
            if (consumer.shouldCheckpoint()) {
                close()
            }
        }
        if (!isClosed.get() && rowCount < limit) {
            finalState.set(CursorState(CursorState.Progress.DONE, listOf()))
        } else {
            val currentCursorValues: List<Serializable> = cursorColNames.mapIndexed { i, colName ->
                val obj: Any? = currentRow[i]
                if (obj == null) {
                    throw IllegalStateException("unexpected null cursor value for $colName")
                }
                if (obj !is Serializable) {
                    throw IllegalStateException("$colName value $obj is of type ${obj.javaClass}" +
                        " which does not implement ${Serializable::class}")
                }
                obj
            }
            finalState.set(CursorState(CursorState.Progress.ONGOING, currentCursorValues))
        }
        notifyStop()
    }

    internal fun computeLimit(conn: Connection): Int {
        if (initialState.progress == CursorState.Progress.NOT_STARTED) {
            return 1
        }
        val limitResults: ResultSet = conn.createStatement().executeQuery(limitSql)
        if (!limitResults.next()) {
            throw IllegalStateException("no rows in limit computation query")
        }
        return limitResults.getInt(1).coerceAtLeast(1)
    }

    fun interface ResultSetAccessor {
        fun getColumnValue(resultSet: ResultSet, columnIndex: Int): Any?

    }


    class Builder : ProducerComponent.Builder<List<Any?>, CursorState> {

        private lateinit var jdbcDriver: Class<*>
        private lateinit var jdbcUrl: String
        private val jdbcProperties = Properties()
        private lateinit var stream: AirbyteStreamNameNamespacePair
        private lateinit var cursorColNames: List<String>
        private lateinit var dataColNames: List<String>
        private lateinit var limitSql: String
        private var resultSetAccessor = ResultSetAccessor { rs, idx ->
            rs.getObject(idx)
        }

        fun withResultSetAccessor(fn: ResultSetAccessor): Builder = apply {
            resultSetAccessor = fn
        }

        fun withJdbcDriver(driver: Class<*>): Builder = apply {
            jdbcDriver = driver
        }

        fun withJdbcDriver(className: String): Builder = withJdbcDriver(Class.forName(className))

        fun withJdbcUrl(fmt: String, vararg args: Any?): Builder = apply {
            jdbcUrl = String.format(fmt, *args)
        }

        fun withJdbcProperty(key: String, value: String?): Builder = apply {
            jdbcProperties.setProperty(key, value)
        }

        fun withAirbyteStream(airbyteStream: ConfiguredAirbyteStream): Builder = apply {
            stream = AirbyteStreamNameNamespacePair(airbyteStream.stream.name, airbyteStream.stream.namespace)
            cursorColNames = airbyteStream.stream.sourceDefinedPrimaryKey.map { it[0] }
            dataColNames = CatalogHelpers.getTopLevelFieldNames(airbyteStream).toList().sorted()
        }

        fun withCursorColumn(name: String): Builder = apply {
            cursorColNames.addLast(name)
        }

        fun withDataColumn(name: String): Builder = apply {
            dataColNames.addLast(name)
        }

        fun withLimitSql(fmt: String, vararg args: Any?): Builder = apply {
            limitSql = String.format(fmt, *args)
        }

        override fun build(
            input: CursorState,
            consumer: ConsumerComponent<List<Any?>, *>,
            notifyStop: () -> Unit
        ): ProducerComponent<CursorState> =
            CursorProducer(jdbcDriver, jdbcUrl, jdbcProperties, stream, cursorColNames, dataColNames, limitSql, resultSetAccessor, consumer, notifyStop, input)
    }
}
