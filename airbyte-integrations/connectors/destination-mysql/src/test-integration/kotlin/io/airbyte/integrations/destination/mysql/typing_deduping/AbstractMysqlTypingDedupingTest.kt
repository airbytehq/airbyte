/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest
import io.airbyte.commons.text.Names
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.destination.mysql.MySQLDestination
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer
import io.airbyte.integrations.destination.mysql.MysqlTestDatabase
import io.airbyte.integrations.destination.mysql.MysqlTestSourceOperations
import javax.sql.DataSource
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.impl.DSL.name
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll

abstract class AbstractMysqlTypingDedupingTest : JdbcTypingDedupingTest(SQLDialect.MYSQL) {
    override val imageName = "airbyte/destination-mysql:dev"
    override val sqlGenerator = MysqlSqlGenerator()
    override val sourceOperations = MysqlTestSourceOperations()
    override val nameTransformer = MySQLNameTransformer()
    override fun getBaseConfig(): ObjectNode = containerizedConfig.deepCopy()

    override fun getDataSource(config: JsonNode?): DataSource =
        MySQLDestination().getDataSource(bareMetalConfig)

    override fun getDefaultSchema(config: JsonNode): String {
        return config["database"].asText()
    }

    override fun setDefaultSchema(config: JsonNode, schema: String?) {
        (config as ObjectNode).put("database", schema)
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDefaultSchema(config!!)
        }
        // Wrap in getIdentifier as a hack for weird mysql name transformer behavior
        val tableName =
            nameTransformer.getIdentifier(
                nameTransformer.convertStreamName(
                    concatenateRawTableName(
                        streamNamespace,
                        Names.toAlphanumericAndUnderscore(streamName),
                    ),
                ),
            )
        val schema = rawSchema
        return database!!.queryJsons(dslContext.selectFrom(name(schema, tableName)).sql)
    }

    @Throws(Exception::class)
    override fun teardownStreamAndNamespace(streamNamespace: String?, streamName: String) {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDefaultSchema(config!!)
        }
        database!!.execute(
            dslContext
                .dropTableIfExists(
                    name(
                        rawSchema,
                        // Wrap in getIdentifier as a hack for weird mysql name transformer behavior
                        nameTransformer.getIdentifier(
                            concatenateRawTableName(
                                streamNamespace,
                                streamName,
                            ),
                        ),
                    ),
                )
                .sql,
        )

        // mysql doesn't have schemas, it only has databases.
        // so override this method to use dropDatabase.
        database!!.execute(
            dslContext.dropDatabaseIfExists(streamNamespace).getSQL(ParamType.INLINED)
        )
    }

    companion object {
        private lateinit var testContainer: MysqlTestDatabase
        /** The config with host/port accessible from other containers */
        private lateinit var containerizedConfig: ObjectNode
        /**
         * The config with host/port accessible from the host's network. (technically, this is still
         * within the airbyte-ci container, but `containerizedConfig` is intended for containers in
         * the docker-in-docker matryoshka doll)
         */
        private lateinit var bareMetalConfig: ObjectNode

        @JvmStatic
        @BeforeAll
        @Throws(Exception::class)
        fun setupMysql() {
            testContainer = MysqlTestDatabase.`in`(MysqlTestDatabase.BaseImage.MYSQL_8)
            containerizedConfig =
                testContainer
                    .configBuilder()
                    .withDatabase()
                    .withResolvedHostAndPort()
                    .withCredentials()
                    .withoutSsl()
                    .build()
            bareMetalConfig =
                testContainer
                    .configBuilder()
                    .withDatabase()
                    .withHostAndPort()
                    .withCredentials()
                    .withoutSsl()
                    .build()
        }

        @JvmStatic
        @AfterAll
        fun teardownMysql() {
            // Intentionally do nothing.
            // The testcontainer will die at the end of the test run.
        }
    }
}
