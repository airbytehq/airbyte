/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.commons.text.Names
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import javax.sql.DataSource
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.jooq.impl.DSL
import org.jooq.impl.DSL.name

/**
 * This class is largely the same as
 * [io.airbyte.integrations.destination.snowflake.typing_deduping.AbstractSnowflakeTypingDedupingTest]
 * . But (a) it uses jooq to construct the sql statements, and (b) it doesn't need to upcase
 * anything. At some point we might (?) want to do a refactor to combine them.
 */
abstract class JdbcTypingDedupingTest(dialect: SQLDialect = SQLDialect.DEFAULT) :
    BaseTypingDedupingTest() {
    protected var database: JdbcDatabase? = null
    private var dataSource: DataSource? = null
    protected val dslContext: DSLContext = DSL.using(dialect)
    protected open val nameTransformer: NamingConventionTransformer = StandardNameTransformer()

    /**
     * Get the config as declared in GSM (or directly from the testcontainer). This class will do
     * further modification to the config to ensure test isolation.
     *
     * This getter MUST return a new instance on every invocation. Subclasses MAY modify the config
     * object, so we want to prevent them from modifying the base config. The easiest way to achieve
     * this is by returning `yourBaseConfig.deepCopy()`.
     */
    protected abstract fun getBaseConfig(): ObjectNode

    protected abstract fun getDataSource(config: JsonNode?): DataSource?

    protected open val sourceOperations: JdbcCompatibleSourceOperations<*>
        /**
         * Subclasses may need to return a custom source operations if the default one does not
         * handle vendor-specific types correctly. For example, you most likely need to override
         * this method to deserialize JSON columns to JsonNode.
         */
        get() = JdbcUtils.defaultSourceOperations

    protected open val rawSchema: String
        /**
         * Subclasses using a config with a nonstandard raw table schema should override this
         * method.
         */
        get() = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE

    /**
     * Subclasses using a config where the default schema is not in the `schema` key should override
     * this method and [.setDefaultSchema].
     */
    protected open fun getDefaultSchema(config: JsonNode): String {
        return config["schema"].asText()
    }

    /**
     * Subclasses using a config where the default schema is not in the `schema` key should override
     * this method and [.getDefaultSchema].
     */
    protected open fun setDefaultSchema(config: JsonNode, schema: String?) {
        (config as ObjectNode).put("schema", schema)
    }

    override fun generateConfig(): JsonNode? {
        val config: JsonNode = getBaseConfig()
        setDefaultSchema(config, "typing_deduping_default_schema$uniqueSuffix")
        dataSource = getDataSource(config)
        database = DefaultJdbcDatabase(dataSource!!, sourceOperations)
        return config
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDefaultSchema(config!!)
        }
        val tableName =
            nameTransformer.convertStreamName(
                concatenateRawTableName(
                    streamNamespace,
                    Names.toAlphanumericAndUnderscore(streamName),
                ),
            )
        val schema = rawSchema
        return database!!.queryJsons(dslContext.selectFrom(name(schema, tableName)).sql)
    }

    @Throws(Exception::class)
    override fun dumpFinalTableRecords(
        streamNamespace: String?,
        streamName: String
    ): List<JsonNode> {
        var streamNamespace = streamNamespace
        if (streamNamespace == null) {
            streamNamespace = getDefaultSchema(config!!)
        }
        return database!!.queryJsons(
            dslContext
                .selectFrom(name(streamNamespace, Names.toAlphanumericAndUnderscore(streamName)))
                .sql
        )
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
                        nameTransformer.convertStreamName(
                            concatenateRawTableName(
                                streamNamespace,
                                streamName,
                            ),
                        ),
                    ),
                )
                .cascade()
                .sql,
        )
        database!!.execute(dslContext.dropSchemaIfExists(name(streamNamespace)).cascade().sql)
    }

    @Throws(Exception::class)
    override fun globalTeardown() {
        close(dataSource)
    }
}
