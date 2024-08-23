package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.google.errorprone.annotations.MustBeClosed
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.integrations.destination.snowflake.SnowflakeSourceOperations
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.util.stream.Stream
import javax.sql.DataSource
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SnowflakeDatabaseManager(
    private val dataSource: DataSource
) {

    //TODO: Remove temporary code added for testing

    @Throws(SQLException::class)
    fun queryJsons_Local_Wrapper(sql: String?, vararg params: String): List<JsonNode> {
        unsafeQuery_Local_Wrapper(sql, *params).use { stream ->
            return stream.toList()
        }
    }

    //TODO: Remove temporary code added for testing

    /**
     * It is "unsafe" because the caller must manually close the returned stream. Otherwise, there
     * will be a database connection leak.
     */
    @MustBeClosed
    @Throws(SQLException::class)
    fun unsafeQuery_Local_Wrapper(sql: String?, vararg params: String): Stream<JsonNode> {
        return unsafeQuery_Local_Helper(
            { connection: Connection ->
                val statement = connection.prepareStatement(sql)
                var i = 1
                for (param in params) {
                    statement.setString(i, param)
                    ++i
                }
                statement
            },
            { queryResult: ResultSet -> SnowflakeSourceOperations().rowToJson(queryResult) }
        )
    }


    //TODO: Remove temporary code added for testing


    /**
     * You CANNOT assume that data will be returned from this method before the entire [ResultSet]
     * is buffered in memory. Review the implementation of the database's JDBC driver or use the
     * StreamingJdbcDriver if you need this guarantee. The caller should close the returned stream
     * to release the database connection.
     *
     * @param statementCreator create a [PreparedStatement] from a [Connection].
     * @param recordTransform transform each record of that result set into the desired type. do NOT
     * just pass the [ResultSet] through. it is a stateful object will not be accessible if returned
     * from recordTransform.
     * @param <T> type that each record will be mapped to.
     * @return Result of the query mapped to a stream.
     * @throws SQLException SQL related exceptions. </T>
     */
    @MustBeClosed
    @Throws(SQLException::class)
    fun <T> unsafeQuery_Local_Helper(
        statementCreator: CheckedFunction<Connection, PreparedStatement, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): Stream<T> {

        var connection = dataSource.connection

        if(connection != null) {
            println(connection)
        }

        try {

            return JdbcDatabase.Companion.toUnsafeStream<T>(
                statementCreator.apply(connection).executeQuery(),
                recordTransform
            )
                .onClose(
                    Runnable {
                        try {
                            LOGGER.info("closing connection")
                            connection.close()
                        } catch (e: SQLException) {
                            throw RuntimeException(e)
                        }
                    }
                )

        } catch (e: Throwable) {

            if (connection != null) {
                connection.close()
            }

            throw e

        }

    }

    //------- End of code added for testing

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(SnowflakeDestinationHandler::class.java)
    }

}
