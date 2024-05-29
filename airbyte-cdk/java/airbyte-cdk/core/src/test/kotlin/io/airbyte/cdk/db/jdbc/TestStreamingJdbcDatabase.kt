/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig
import io.airbyte.cdk.db.jdbc.streaming.FetchSizeConstants
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import java.sql.*
import java.util.Map
import java.util.concurrent.atomic.AtomicReference
import org.junit.jupiter.api.*
import org.mockito.Mockito
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

@TestMethodOrder(MethodOrderer.OrderAnnotation::class)
internal class TestStreamingJdbcDatabase {
    private val sourceOperations: JdbcSourceOperations = JdbcUtils.defaultSourceOperations
    private var defaultJdbcDatabase: JdbcDatabase? = null
    private var streamingJdbcDatabase: JdbcDatabase? = null

    @BeforeEach
    fun setup() {
        val dbName = Strings.addRandomSuffix("db", "_", 10)

        val config = getConfig(PSQL_DB, dbName)

        val initScriptName = "init_$dbName.sql"
        val tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE $dbName;")
        PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB)

        val connectionPool =
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

        defaultJdbcDatabase = Mockito.spy(DefaultJdbcDatabase(connectionPool))
        streamingJdbcDatabase =
            StreamingJdbcDatabase(connectionPool, JdbcUtils.defaultSourceOperations) { ->
                AdaptiveStreamingQueryConfig()
            }
    }

    @Test
    @Order(1)
    @Throws(SQLException::class)
    fun testQuery() {
        defaultJdbcDatabase!!.execute { connection: Connection ->
            connection
                .createStatement()
                .execute(
                    """
          DROP TABLE IF EXISTS id_and_name;
          CREATE TABLE id_and_name (id INTEGER, name VARCHAR(200));
          INSERT INTO id_and_name (id, name) VALUES (1, 'picard'),  (2, 'crusher'), (3, 'vash');
          
          """.trimIndent()
                )
        }

        // grab references to connection and prepared statement, so we can verify the streaming
        // config is
        // invoked.
        val connection1 = AtomicReference<Connection>()
        val ps1 = AtomicReference<PreparedStatement>()
        val actual =
            streamingJdbcDatabase!!.queryJsons(
                { connection: Connection ->
                    connection1.set(connection)
                    val ps = connection.prepareStatement("SELECT * FROM id_and_name;")
                    ps1.set(ps)
                    ps
                },
                { queryContext: ResultSet -> sourceOperations.rowToJson(queryContext) }
            )
        val expectedRecords: List<JsonNode> =
            Lists.newArrayList(
                Jsons.jsonNode(Map.of("id", 1, "name", "picard")),
                Jsons.jsonNode(Map.of("id", 2, "name", "crusher")),
                Jsons.jsonNode(Map.of("id", 3, "name", "vash"))
            )
        Assertions.assertEquals(expectedRecords, actual)
    }

    /**
     * Test stream querying a table with 20 rows. Each row is 10 MB large. The table in this test
     * must contain more than `FetchSizeConstants.INITIAL_SAMPLE_SIZE` rows. Otherwise, all rows
     * will be fetched in the first fetch, the fetch size won't be adjusted, and the test will fail.
     */
    @Order(2)
    @Test
    @Throws(SQLException::class)
    fun testLargeRow() {
        defaultJdbcDatabase!!.execute { connection: Connection ->
            connection
                .createStatement()
                .execute(
                    """
            DROP TABLE IF EXISTS id_and_name;
            CREATE TABLE id_and_name (id INTEGER, name TEXT);
            INSERT INTO id_and_name SELECT id, repeat('a', 10485760) as name from generate_series(1, 20) as id;
            
            """.trimIndent()
                )
        }

        val connection1 = AtomicReference<Connection>()
        val ps1 = AtomicReference<PreparedStatement>()
        val fetchSizes: MutableSet<Int> = HashSet()
        val actual =
            streamingJdbcDatabase!!.queryJsons(
                { connection: Connection ->
                    connection1.set(connection)
                    val ps = connection.prepareStatement("SELECT * FROM id_and_name;")
                    ps1.set(ps)
                    ps
                },
                { resultSet: ResultSet ->
                    fetchSizes.add(resultSet.fetchSize)
                    sourceOperations.rowToJson(resultSet)
                }
            )
        Assertions.assertEquals(20, actual.size)

        // Two fetch sizes should be set on the result set, one is the initial sample size,
        // and the other is smaller than the initial value because of the large row.
        // This check assumes that FetchSizeConstants.TARGET_BUFFER_BYTE_SIZE = 200 MB.
        // Update this check if the buffer size constant is changed.
        Assertions.assertEquals(2, fetchSizes.size)
        val sortedSizes = fetchSizes.sorted()
        Assertions.assertTrue(sortedSizes[0] < FetchSizeConstants.INITIAL_SAMPLE_SIZE)
        Assertions.assertEquals(FetchSizeConstants.INITIAL_SAMPLE_SIZE, sortedSizes[1])
    }

    private fun getConfig(psqlDb: PostgreSQLContainer<*>?, dbName: String): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.HOST_KEY, psqlDb!!.host)
                .put(JdbcUtils.PORT_KEY, psqlDb.firstMappedPort)
                .put(JdbcUtils.DATABASE_KEY, dbName)
                .put(JdbcUtils.USERNAME_KEY, psqlDb.username)
                .put(JdbcUtils.PASSWORD_KEY, psqlDb.password)
                .build()
        )
    }

    companion object {
        private lateinit var PSQL_DB: PostgreSQLContainer<Nothing>

        @JvmStatic
        @BeforeAll
        fun init(): Unit {
            PSQL_DB = PostgreSQLContainer<Nothing>("postgres:13-alpine")
            PSQL_DB.start()
        }

        @JvmStatic
        @AfterAll
        fun cleanUp(): Unit {
            PSQL_DB.close()
        }
    }
}
