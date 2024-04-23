/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.BinaryNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.base.Charsets
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.MoreStreams
import io.airbyte.commons.string.Strings
import io.airbyte.protocol.models.JsonSchemaType
import java.math.BigDecimal
import java.sql.*
import java.util.stream.Collectors
import javax.sql.DataSource
import org.bouncycastle.util.encoders.Base64
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

internal class TestJdbcUtils {
    private var dbName: String = "dummy"
    private lateinit var dataSource: DataSource
    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        dbName = Strings.addRandomSuffix("db", "_", 10)

        val config = getConfig(PSQL_DB, dbName)

        val initScriptName = "init_$dbName.sql"
        val tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE $dbName;")
        PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB)

        dataSource =
            DataSourceFactory.create(
                config[JdbcUtils.USERNAME_KEY].asText(),
                config[JdbcUtils.PASSWORD_KEY].asText(),
                DatabaseDriver.POSTGRESQL.driverClassName,
                String.format(
                    DatabaseDriver.POSTGRESQL.urlFormatString,
                    config[JdbcUtils.HOST_KEY].asText(),
                    config[JdbcUtils.PORT_KEY].asInt(),
                    config[JdbcUtils.DATABASE_KEY].asText()
                )
            )

        val defaultJdbcDatabase: JdbcDatabase = DefaultJdbcDatabase(dataSource)

        defaultJdbcDatabase.execute { connection: Connection ->
            connection
                .createStatement()
                .execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
            connection
                .createStatement()
                .execute(
                    "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
                )
        }
    }

    private fun getConfig(psqlDb: PostgreSQLContainer<*>?, dbName: String?): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.builder<Any, Any?>()
                .put(JdbcUtils.HOST_KEY, psqlDb!!.host)
                .put(JdbcUtils.PORT_KEY, psqlDb.firstMappedPort)
                .put(JdbcUtils.DATABASE_KEY, dbName)
                .put(JdbcUtils.USERNAME_KEY, psqlDb.username)
                .put(JdbcUtils.PASSWORD_KEY, psqlDb.password)
                .build()
        )
    }

    // Takes in a generic sslValue because useSsl maps sslValue to a boolean
    private fun <T> getConfigWithSsl(
        psqlDb: PostgreSQLContainer<*>?,
        dbName: String?,
        sslValue: T
    ): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.builder<Any, Any?>()
                .put("host", psqlDb!!.host)
                .put("port", psqlDb.firstMappedPort)
                .put("database", dbName)
                .put("username", psqlDb.username)
                .put("password", psqlDb.password)
                .put("ssl", sslValue)
                .build()
        )
    }

    @Test
    @Throws(SQLException::class)
    fun testRowToJson() {
        dataSource.connection.use { connection ->
            val rs = connection.createStatement().executeQuery("SELECT * FROM id_and_name;")
            rs.next()
            Assertions.assertEquals(RECORDS_AS_JSON[0], sourceOperations.rowToJson(rs))
        }
    }

    @Test
    @Throws(SQLException::class)
    fun testToStream() {
        dataSource.connection.use { connection ->
            val rs = connection.createStatement().executeQuery("SELECT * FROM id_and_name;")
            val actual =
                JdbcDatabase.toUnsafeStream(rs) { queryContext: ResultSet ->
                        sourceOperations.rowToJson(queryContext)
                    }
                    .collect(Collectors.toList())
            Assertions.assertEquals(RECORDS_AS_JSON, actual)
        }
    }

    // test conversion of every JDBCType that we support to Json.
    @Test
    @Throws(SQLException::class)
    fun testSetJsonField() {
        dataSource.connection.use { connection ->
            createTableWithAllTypes(connection)
            insertRecordOfEachType(connection)
            assertExpectedOutputValues(connection, jsonFieldExpectedValues())
            assertExpectedOutputTypes(connection)
        }
    }

    // test setting on a PreparedStatement every JDBCType that we support.
    @Test
    @Throws(SQLException::class)
    fun testSetStatementField() {
        dataSource.connection.use { connection ->
            createTableWithAllTypes(connection)
            val ps =
                connection.prepareStatement(
                    "INSERT INTO data VALUES(?::bit,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
                )

            // insert the bit here to stay consistent even though setStatementField does not support
            // it yet.
            ps.setString(1, "1")
            sourceOperations.setCursorField(ps, 2, JDBCType.BOOLEAN, "true")
            sourceOperations.setCursorField(ps, 3, JDBCType.SMALLINT, "1")
            sourceOperations.setCursorField(ps, 4, JDBCType.INTEGER, "1")
            sourceOperations.setCursorField(ps, 5, JDBCType.BIGINT, "1")
            sourceOperations.setCursorField(ps, 6, JDBCType.FLOAT, "1.0")
            sourceOperations.setCursorField(ps, 7, JDBCType.DOUBLE, "1.0")
            sourceOperations.setCursorField(ps, 8, JDBCType.REAL, "1.0")
            sourceOperations.setCursorField(ps, 9, JDBCType.NUMERIC, "1")
            sourceOperations.setCursorField(ps, 10, JDBCType.DECIMAL, "1")
            sourceOperations.setCursorField(ps, 11, JDBCType.CHAR, "a")
            sourceOperations.setCursorField(ps, 12, JDBCType.VARCHAR, "a")
            sourceOperations.setCursorField(ps, 13, JDBCType.DATE, "2020-11-01")
            sourceOperations.setCursorField(ps, 14, JDBCType.TIME, "05:00:00.000")
            sourceOperations.setCursorField(ps, 15, JDBCType.TIMESTAMP, "2001-09-29T03:00:00.000")
            sourceOperations.setCursorField(ps, 16, JDBCType.BINARY, "61616161")

            ps.execute()

            assertExpectedOutputValues(connection, expectedValues())
            assertExpectedOutputTypes(connection)
        }
    }

    @Test
    fun testUseSslWithSslNotSet() {
        val config = getConfig(PSQL_DB, dbName)
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertTrue(sslSet)
    }

    @Test
    fun testUseSslWithSslSetAndValueStringFalse() {
        val config = getConfigWithSsl(PSQL_DB, dbName, "false")
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertFalse(sslSet)
    }

    @Test
    fun testUseSslWithSslSetAndValueIntegerFalse() {
        val config = getConfigWithSsl(PSQL_DB, dbName, 0)
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertFalse(sslSet)
    }

    @Test
    fun testUseSslWithSslSetAndValueStringTrue() {
        val config = getConfigWithSsl(PSQL_DB, dbName, "true")
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertTrue(sslSet)
    }

    @Test
    fun testUssSslWithSslSetAndValueIntegerTrue() {
        val config = getConfigWithSsl(PSQL_DB, dbName, 3)
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertTrue(sslSet)
    }

    @Test
    fun testUseSslWithEmptySslKeyAndSslModeVerifyFull() {
        val config =
            Jsons.jsonNode(
                ImmutableMap.builder<Any, Any?>()
                    .put("host", PSQL_DB.host)
                    .put("port", PSQL_DB.firstMappedPort)
                    .put("database", dbName)
                    .put("username", PSQL_DB.username)
                    .put("password", PSQL_DB.password)
                    .put(
                        "ssl_mode",
                        ImmutableMap.builder<Any, Any>()
                            .put("mode", "verify-full")
                            .put("ca_certificate", "test_ca_cert")
                            .put("client_certificate", "test_client_cert")
                            .put("client_key", "test_client_key")
                            .put("client_key_password", "test_pass")
                            .build()
                    )
                    .build()
            )
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertTrue(sslSet)
    }

    @Test
    fun testUseSslWithEmptySslKeyAndSslModeDisable() {
        val config =
            Jsons.jsonNode(
                ImmutableMap.builder<Any, Any?>()
                    .put("host", PSQL_DB.host)
                    .put("port", PSQL_DB.firstMappedPort)
                    .put("database", dbName)
                    .put("username", PSQL_DB.username)
                    .put("password", PSQL_DB.password)
                    .put(
                        "ssl_mode",
                        ImmutableMap.builder<Any, Any>().put("mode", "disable").build()
                    )
                    .build()
            )
        val sslSet = JdbcUtils.useSsl(config)
        Assertions.assertFalse(sslSet)
    }

    private fun jsonFieldExpectedValues(): ObjectNode {
        val expected = expectedValues()
        val arrayNode = ObjectMapper().createArrayNode()
        arrayNode.add("one")
        arrayNode.add("two")
        arrayNode.add("three")
        expected.set<JsonNode>("text_array", arrayNode)

        val arrayNode2 = ObjectMapper().createArrayNode()
        arrayNode2.add("1")
        arrayNode2.add("2")
        arrayNode2.add("3")
        expected.set<JsonNode>("int_array", arrayNode2)

        expected.set<JsonNode>("binary1", BinaryNode("aaaa".toByteArray(Charsets.UTF_8)))

        return expected
    }

    private fun expectedValues(): ObjectNode {
        val expected = Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode
        expected.put("bit", true)
        expected.put("boolean", true)
        expected.put("smallint", 1.toShort())
        expected.put("int", 1)
        expected.put("bigint", 1L)
        expected.put("float", 1.0)
        expected.put("double", 1.0)
        expected.put("real", 1.0.toFloat())
        expected.put("numeric", BigDecimal(1))
        expected.put("decimal", BigDecimal(1))
        expected.put("char", "a")
        expected.put("varchar", "a")
        expected.put("date", "2020-11-01")
        expected.put("time", "05:00:00.000000")
        expected.put("timestamp", "2001-09-29T03:00:00.000000")
        expected.put("binary1", Base64.decode("61616161".toByteArray(Charsets.UTF_8)))
        return expected
    }

    @ParameterizedTest
    @CsvSource(
        "'3E+1', 30",
        "'30', 30",
        "'999000000000', 999000000000",
        "'999E+9', 999000000000",
        "'1.79E+3', 1790"
    )
    @Throws(SQLException::class)
    fun testSetStatementSpecialValues(colValue: String, value: Long) {
        dataSource.connection.use { connection ->
            createTableWithAllTypes(connection)
            val ps = connection.prepareStatement("INSERT INTO data(bigint) VALUES(?);")

            // insert the bit here to stay consistent even though setStatementField does not support
            // it yet.
            sourceOperations.setCursorField(ps, 1, JDBCType.BIGINT, colValue)
            ps.execute()

            assertExpectedOutputValues(
                connection,
                (Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode).put("bigint", value)
            )
            assertExpectedOutputTypes(connection)
        }
    }

    companion object {
        private const val ONE_POINT_0 = "1.0,"

        private val RECORDS_AS_JSON: List<JsonNode> =
            Lists.newArrayList(
                Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")),
                Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")),
                Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash"))
            )

        private lateinit var PSQL_DB: PostgreSQLContainer<Nothing>

        private val sourceOperations: JdbcSourceOperations = JdbcUtils.defaultSourceOperations

        @JvmStatic
        @BeforeAll
        fun init(): Unit {
            PSQL_DB = PostgreSQLContainer<Nothing>("postgres:13-alpine")
            PSQL_DB.start()
        }

        @Throws(SQLException::class)
        private fun createTableWithAllTypes(connection: Connection) {
            // jdbctype not included because they are not directly supported in postgres: TINYINT,
            // LONGVARCHAR,
            // VARBINAR, LONGVARBINARY
            connection
                .createStatement()
                .execute(
                    "CREATE TABLE data(" +
                        "bit BIT, " +
                        "boolean BOOLEAN, " +
                        "smallint SMALLINT," +
                        "int INTEGER," +
                        "bigint BIGINT," +
                        "float FLOAT," +
                        "double DOUBLE PRECISION," +
                        "real REAL," +
                        "numeric NUMERIC," +
                        "decimal DECIMAL," +
                        "char CHAR," +
                        "varchar VARCHAR," +
                        "date DATE," +
                        "time TIME," +
                        "timestamp TIMESTAMP," +
                        "binary1 bytea," +
                        "text_array _text," +
                        "int_array int[]" +
                        ");"
                )
        }

        @Throws(SQLException::class)
        private fun insertRecordOfEachType(connection: Connection) {
            connection
                .createStatement()
                .execute(
                    "INSERT INTO data(" +
                        "bit," +
                        "boolean," +
                        "smallint," +
                        "int," +
                        "bigint," +
                        "float," +
                        "double," +
                        "real," +
                        "numeric," +
                        "decimal," +
                        "char," +
                        "varchar," +
                        "date," +
                        "time," +
                        "timestamp," +
                        "binary1," +
                        "text_array," +
                        "int_array" +
                        ") VALUES(" +
                        "1::bit(1)," +
                        "true," +
                        "1," +
                        "1," +
                        "1," +
                        ONE_POINT_0 +
                        ONE_POINT_0 +
                        ONE_POINT_0 +
                        "1," +
                        ONE_POINT_0 +
                        "'a'," +
                        "'a'," +
                        "'2020-11-01'," +
                        "'05:00'," +
                        "'2001-09-29 03:00'," +
                        "decode('61616161', 'hex')," +
                        "'{one,two,three}'," +
                        "'{1,2,3}'" +
                        ");"
                )
        }

        @Throws(SQLException::class)
        private fun assertExpectedOutputValues(connection: Connection, expected: ObjectNode) {
            val resultSet = connection.createStatement().executeQuery("SELECT * FROM data;")

            resultSet.next()
            val actual = sourceOperations.rowToJson(resultSet)

            // field-wise comparison to make debugging easier.
            MoreStreams.toStream(expected.fields()).forEach { e: Map.Entry<String, JsonNode?> ->
                Assertions.assertEquals(e.value, actual[e.key], "key: " + e.key)
            }
            Assertions.assertEquals(expected, actual)
        }

        @Throws(SQLException::class)
        private fun assertExpectedOutputTypes(connection: Connection) {
            val resultSet = connection.createStatement().executeQuery("SELECT * FROM data;")

            resultSet.next()
            val columnCount = resultSet.metaData.columnCount
            val actual: MutableMap<String, JsonSchemaType> = HashMap(columnCount)
            for (i in 1..columnCount) {
                actual[resultSet.metaData.getColumnName(i)] =
                    sourceOperations.getAirbyteType(
                        JDBCType.valueOf(resultSet.metaData.getColumnType(i))
                    )
            }

            val expected: Map<String, JsonSchemaType> =
                ImmutableMap.builder<String, JsonSchemaType>()
                    .put("bit", JsonSchemaType.BOOLEAN)
                    .put("boolean", JsonSchemaType.BOOLEAN)
                    .put("smallint", JsonSchemaType.INTEGER)
                    .put("int", JsonSchemaType.INTEGER)
                    .put("bigint", JsonSchemaType.INTEGER)
                    .put("float", JsonSchemaType.NUMBER)
                    .put("double", JsonSchemaType.NUMBER)
                    .put("real", JsonSchemaType.NUMBER)
                    .put("numeric", JsonSchemaType.NUMBER)
                    .put("decimal", JsonSchemaType.NUMBER)
                    .put("char", JsonSchemaType.STRING)
                    .put("varchar", JsonSchemaType.STRING)
                    .put("date", JsonSchemaType.STRING)
                    .put("time", JsonSchemaType.STRING)
                    .put("timestamp", JsonSchemaType.STRING)
                    .put("binary1", JsonSchemaType.STRING_BASE_64)
                    .put("text_array", JsonSchemaType.ARRAY)
                    .put("int_array", JsonSchemaType.ARRAY)
                    .build()

            Assertions.assertEquals(actual, expected)
        }
    }
}
