/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.DataTypeUtils
import io.airbyte.cdk.db.DbAnalyticsUtils.dataTypesSerializationErrorMessage
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.sql.*
import java.sql.Date
import java.text.ParseException
import java.time.*
import java.time.chrono.IsoEra
import java.time.format.DateTimeParseException
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** Source operation skeleton for JDBC compatible databases. */
abstract class AbstractJdbcCompatibleSourceOperations<Datatype> :
    JdbcCompatibleSourceOperations<Datatype> {

    private val LOGGER: Logger =
        LoggerFactory.getLogger(AbstractJdbcCompatibleSourceOperations::class.java)

    @Throws(SQLException::class)
    override fun convertDatabaseRowToAirbyteRecordData(queryContext: ResultSet): AirbyteRecordData {
        // the first call communicates with the database. after that the result is cached.
        val columnCount = queryContext.metaData.columnCount
        val jsonNode = Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode
        val metaChanges: MutableList<AirbyteRecordMessageMetaChange> =
            ArrayList<AirbyteRecordMessageMetaChange>()

        for (i in 1..columnCount) {
            val columnName = queryContext.metaData.getColumnName(i)
            val columnTypeName = queryContext.metaData.getColumnTypeName(i)
            try {
                // convert to java types that will convert into reasonable json.
                copyToJsonField(queryContext, i, jsonNode)
            } catch (e: java.lang.Exception) {
                jsonNode.putNull(columnName)
                LOGGER.info(
                    "Failed to serialize column: {}, of type {}, with error {}",
                    columnName,
                    columnTypeName,
                    e.message
                )
                AirbyteTraceMessageUtility.emitAnalyticsTrace(dataTypesSerializationErrorMessage())
                metaChanges.add(
                    AirbyteRecordMessageMetaChange()
                        .withField(columnName)
                        .withChange(AirbyteRecordMessageMetaChange.Change.NULLED)
                        .withReason(
                            AirbyteRecordMessageMetaChange.Reason.SOURCE_SERIALIZATION_ERROR,
                        ),
                )
            }
        }

        return AirbyteRecordData(jsonNode, AirbyteRecordMessageMeta().withChanges(metaChanges))
    }
    @Throws(SQLException::class)
    override fun rowToJson(queryResult: ResultSet): JsonNode {
        // the first call communicates with the database. after that the result is cached.
        val columnCount = queryResult.metaData.columnCount
        val jsonNode = Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode

        for (i in 1..columnCount) {
            // attempt to access the column. this allows us to know if it is null before we do
            // type-specific
            // parsing. if it is null, we can move on. while awkward, this seems to be the agreed
            // upon way of
            // checking for null values with jdbc.
            queryResult.getObject(i)
            if (queryResult.wasNull()) {
                continue
            }

            // convert to java types that will convert into reasonable json.
            copyToJsonField(queryResult, i, jsonNode)
        }

        return jsonNode
    }

    @Throws(SQLException::class)
    protected fun putArray(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        val arrayNode = ObjectMapper().createArrayNode()
        val arrayResultSet = resultSet.getArray(index).resultSet
        while (arrayResultSet.next()) {
            arrayNode.add(arrayResultSet.getString(2))
        }
        node.set<JsonNode>(columnName, arrayNode)
    }

    @Throws(SQLException::class)
    protected open fun putBoolean(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, resultSet.getBoolean(index))
    }

    /**
     * In some sources Short might have value larger than [Short.MAX_VALUE]. E.q. MySQL has unsigned
     * smallint type, which can contain value 65535. If we fail to cast Short value, we will try to
     * cast Integer.
     */
    @Throws(SQLException::class)
    protected fun putShortInt(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        try {
            node.put(columnName, resultSet.getShort(index))
        } catch (e: SQLException) {
            node.put(columnName, DataTypeUtils.returnNullIfInvalid { resultSet.getInt(index) })
        }
    }

    /**
     * In some sources Integer might have value larger than [Integer.MAX_VALUE]. E.q. MySQL has
     * unsigned Integer type, which can contain value 3428724653. If we fail to cast Integer value,
     * we will try to cast Long.
     */
    @Throws(SQLException::class)
    protected fun putInteger(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        try {
            node.put(columnName, resultSet.getInt(index))
        } catch (e: SQLException) {
            node.put(columnName, DataTypeUtils.returnNullIfInvalid { resultSet.getLong(index) })
        }
    }

    @Throws(SQLException::class)
    protected fun putBigInt(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, DataTypeUtils.returnNullIfInvalid { resultSet.getLong(index) })
    }

    @Throws(SQLException::class)
    protected open fun putDouble(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(
            columnName,
            DataTypeUtils.returnNullIfInvalid(
                { resultSet.getDouble(index) },
                { d: Double -> java.lang.Double.isFinite(d) },
            ),
        )
    }

    @Throws(SQLException::class)
    protected fun putFloat(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(
            columnName,
            DataTypeUtils.returnNullIfInvalid(
                { resultSet.getFloat(index) },
                { f: Float -> java.lang.Float.isFinite(f) },
            ),
        )
    }

    @Throws(SQLException::class)
    protected open fun putBigDecimal(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, DataTypeUtils.returnNullIfInvalid { resultSet.getBigDecimal(index) })
    }

    @Throws(SQLException::class)
    protected fun putString(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, resultSet.getString(index))
    }

    @Throws(SQLException::class)
    protected open fun putDate(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, resultSet.getString(index))
    }

    @Throws(SQLException::class)
    protected open fun putTime(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(
            columnName,
            DateTimeConverter.convertToTime(getObject(resultSet, index, LocalTime::class.java)),
        )
    }

    @Throws(SQLException::class)
    protected open fun putTimestamp(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        try {
            node.put(
                columnName,
                DateTimeConverter.convertToTimestamp(
                    getObject(resultSet, index, LocalDateTime::class.java),
                ),
            )
        } catch (e: Exception) {
            // for backward compatibility
            val instant = resultSet.getTimestamp(index).toInstant()
            node.put(columnName, DataTypeUtils.toISO8601StringWithMicroseconds(instant))
        }
    }

    @Throws(SQLException::class)
    protected open fun putBinary(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, resultSet.getBytes(index))
    }

    @Throws(SQLException::class)
    protected fun putDefault(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        node.put(columnName, resultSet.getString(index))
    }

    @Throws(SQLException::class)
    protected fun setTime(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String?
    ) {
        try {
            preparedStatement.setObject(parameterIndex, LocalTime.parse(value))
        } catch (e: DateTimeParseException) {
            setTimestamp(preparedStatement, parameterIndex, value)
        }
    }

    @Throws(SQLException::class)
    protected open fun setTimestamp(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String?
    ) {
        try {
            preparedStatement.setObject(parameterIndex, LocalDateTime.parse(value))
        } catch (e: DateTimeParseException) {
            preparedStatement.setObject(parameterIndex, OffsetDateTime.parse(value))
        }
    }

    @Throws(SQLException::class)
    protected open fun setDate(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        try {
            preparedStatement.setObject(parameterIndex, LocalDate.parse(value))
        } catch (e: DateTimeParseException) {
            setDateAsTimestamp(preparedStatement, parameterIndex, value)
        }
    }

    @Throws(SQLException::class)
    private fun setDateAsTimestamp(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        try {
            val from = Timestamp.from(DataTypeUtils.dateFormat.parse(value).toInstant())
            preparedStatement.setDate(parameterIndex, Date(from.time))
        } catch (e: ParseException) {
            throw RuntimeException(e)
        }
    }

    @Throws(SQLException::class)
    protected open fun setBit(
        preparedStatement: PreparedStatement?,
        parameterIndex: Int,
        value: String?
    ) {
        // todo (cgardens) - currently we do not support bit because it requires special handling in
        // the
        // prepared statement.
        // see
        // https://www.postgresql-archive.org/Problems-with-BIT-datatype-and-preparedStatment-td5733533.html.
        throw RuntimeException("BIT value is not supported as incremental parameter!")
    }

    @Throws(SQLException::class)
    protected fun setBoolean(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setBoolean(parameterIndex, value.toBoolean())
    }

    @Throws(SQLException::class)
    protected fun setShortInt(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setShort(parameterIndex, value.toShort())
    }

    @Throws(SQLException::class)
    protected fun setInteger(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setInt(parameterIndex, value.toInt())
    }

    @Throws(SQLException::class)
    protected fun setBigInteger(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setLong(parameterIndex, BigDecimal(value).toBigInteger().toLong())
    }

    @Throws(SQLException::class)
    protected fun setDouble(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setDouble(parameterIndex, value.toDouble())
    }

    @Throws(SQLException::class)
    protected fun setReal(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setFloat(parameterIndex, value.toFloat())
    }

    @Throws(SQLException::class)
    protected fun setDecimal(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String
    ) {
        preparedStatement.setBigDecimal(parameterIndex, BigDecimal(value))
    }

    @Throws(SQLException::class)
    protected fun setString(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String?
    ) {
        preparedStatement.setString(parameterIndex, value)
    }

    @Throws(SQLException::class)
    protected fun setBinary(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        value: String?
    ) {
        preparedStatement.setBytes(parameterIndex, Base64.getDecoder().decode(value))
    }

    @Throws(SQLException::class)
    protected fun <ObjectType> getObject(
        resultSet: ResultSet,
        index: Int,
        clazz: Class<ObjectType>?
    ): ObjectType {
        return resultSet.getObject(index, clazz)
    }

    @Throws(SQLException::class)
    protected open fun putTimeWithTimezone(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        val timetz = getObject(resultSet, index, OffsetTime::class.java)
        node.put(columnName, DateTimeConverter.convertToTimeWithTimezone(timetz))
    }

    @Throws(SQLException::class)
    protected open fun putTimestampWithTimezone(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        val timestamptz = getObject(resultSet, index, OffsetDateTime::class.java)
        val localDate = timestamptz.toLocalDate()
        node.put(
            columnName,
            resolveEra(localDate, timestamptz.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)),
        )
    }

    companion object {
        /** A Date representing the earliest date in CE. Any date before this is in BCE. */
        private val ONE_CE: Date = Date.valueOf("0001-01-01")

        /**
         * Modifies a string representation of a date/timestamp and normalizes its era indicator.
         * Specifically, if this is a BCE value:
         *
         * * The leading negative sign will be removed if present
         * * The "BC" suffix will be appended, if not already present
         *
         * You most likely would prefer to call one of the overloaded methods, which accept temporal
         * types.
         */
        fun resolveEra(isBce: Boolean, value: String): String {
            var mangledValue = value
            if (isBce) {
                if (mangledValue.startsWith("-")) {
                    mangledValue = mangledValue.substring(1)
                }
                if (!mangledValue.endsWith(" BC")) {
                    mangledValue += " BC"
                }
            }
            return mangledValue
        }

        fun isBce(date: LocalDate): Boolean {
            return date.era == IsoEra.BCE
        }

        @JvmStatic
        fun resolveEra(date: LocalDate, value: String): String {
            return resolveEra(isBce(date), value)
        }

        /**
         * java.sql.Date objects don't properly represent their era (for example, using
         * toLocalDate() always returns an object in CE). So to determine the era, we just check
         * whether the date is before 1 AD.
         *
         * This is technically kind of sketchy due to ancient timestamps being weird (leap years,
         * etc.), but my understanding is that [.ONE_CE] has the same weirdness, so it cancels out.
         */
        @JvmStatic
        fun resolveEra(date: Date, value: String): String {
            return resolveEra(date.before(ONE_CE), value)
        }

        /** See [.resolveEra] for explanation. */
        @JvmStatic
        fun resolveEra(timestamp: Timestamp, value: String): String {
            return resolveEra(timestamp.before(ONE_CE), value)
        }
    }
}
