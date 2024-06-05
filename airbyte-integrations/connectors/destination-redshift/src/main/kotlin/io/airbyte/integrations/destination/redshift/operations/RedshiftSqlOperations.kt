/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.operations

import com.google.common.collect.Iterables
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperationsUtils.insertRawRecordsInSingleQuery
import io.airbyte.commons.json.Jsons.serialize
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.sql.SQLException
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.*
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.conf.Settings
import org.jooq.conf.StatementType
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType
import org.slf4j.Logger
import org.slf4j.LoggerFactory

open class RedshiftSqlOperations : JdbcSqlOperations() {
    private val dslContext: DSLContext
        get() = DSL.using(SQLDialect.POSTGRES)

    override fun createTableQueryV1(schemaName: String?, tableName: String?): String {
        return String.format(
            """
                         CREATE TABLE IF NOT EXISTS %s.%s (
                          %s VARCHAR PRIMARY KEY,
                          %s SUPER,
                          %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
                          
                          """.trimIndent(),
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT
        )
    }

    override fun createTableQueryV2(schemaName: String?, tableName: String?): String {
        val dsl = dslContext
        return dsl.createTableIfNotExists(DSL.name(schemaName, tableName))
            .column(
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                SQLDataType.VARCHAR(36).nullable(false)
            )
            .column(
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                SQLDataType.TIMESTAMPWITHTIMEZONE.defaultValue(
                    DSL.function<OffsetDateTime>("GETDATE", SQLDataType.TIMESTAMPWITHTIMEZONE)
                )
            )
            .column(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE)
            .column(
                JavaBaseConstants.COLUMN_NAME_DATA,
                RedshiftDestinationConstants.SUPER_TYPE.nullable(false)
            )
            .column(
                JavaBaseConstants.COLUMN_NAME_AB_META,
                RedshiftDestinationConstants.SUPER_TYPE.nullable(true)
            )
            .getSQL()
    }

    @Throws(SQLException::class)
    public override fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tmpTableName: String?
    ) {
        LOGGER.info("actual size of batch: {}", records.size)

        // query syntax:
        // INSERT INTO public.users (ab_id, data, emitted_at) VALUES
        // (?, ?::jsonb, ?),
        // ...
        val insertQueryComponent =
            String.format(
                "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
                schemaName,
                tmpTableName,
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT
            )
        val recordQueryComponent = "(?, JSON_PARSE(?), ?),\n"
        insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records)
    }

    override fun insertRecordsInternalV2(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        try {
            database.execute { connection: Connection ->
                LOGGER.info("Total records received to insert: {}", records.size)
                // This comment was copied from DV1 code
                // (SqlOperationsUtils.insertRawRecordsInSingleQuery):
                // > We also partition the query to run on 10k records at a time, since some DBs set
                // a max limit on
                // > how many records can be inserted at once
                // > TODO(sherif) this should use a smarter, destination-aware partitioning scheme
                // instead of 10k by
                // > default
                for (batch in Iterables.partition<PartialAirbyteMessage>(records, 10000)) {
                    val create =
                        DSL.using(
                            connection,
                            SQLDialect.POSTGRES, // Force inlined params.
                            // jooq normally tries to intelligently use bind params when possible.
                            // This would cause queries with many params to use inline params,
                            // but small queries would use bind params.
                            // In turn, that would force us to intelligently escape string values,
                            // since we need to escape inlined strings
                            // but need to not escape bound strings.
                            // Instead, we force jooq to always inline params,
                            // and always call escapeStringLiteral() on the string values.
                            Settings().withStatementType(StatementType.STATIC_STATEMENT)
                        )
                    // JOOQ adds some overhead here. Building the InsertValuesStep object takes
                    // about 139ms for 5K
                    // records.
                    // That's a nontrivial execution speed loss when the actual statement execution
                    // takes 500ms.
                    // Hopefully we're executing these statements infrequently enough in a sync that
                    // it doesn't matter.
                    // But this is a potential optimization if we need to eke out a little more
                    // performance on standard
                    // inserts.
                    // ... which presumably we won't, because standard inserts is so inherently
                    // slow.
                    // See
                    // https://github.com/airbytehq/airbyte/blob/f73827eb43f62ee30093451c434ad5815053f32d/airbyte-integrations/connectors/destination-redshift/src/main/java/io/airbyte/integrations/destination/redshift/operations/RedshiftSqlOperations.java#L39
                    // and
                    // https://github.com/airbytehq/airbyte/blob/f73827eb43f62ee30093451c434ad5815053f32d/airbyte-cdk/java/airbyte-cdk/db-destinations/src/main/java/io/airbyte/cdk/integrations/destination/jdbc/SqlOperationsUtils.java#L62
                    // for how DV1 did this in pure JDBC.
                    var insert =
                        create.insertInto<
                            Record?, String?, String?, String?, OffsetDateTime?, OffsetDateTime?>(
                            DSL.table(DSL.name(schemaName, tableName)),
                            DSL.field<String>(
                                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                                SQLDataType.VARCHAR(36)
                            ),
                            DSL.field<String>(
                                JavaBaseConstants.COLUMN_NAME_DATA,
                                RedshiftDestinationConstants.SUPER_TYPE
                            ),
                            DSL.field<String>(
                                JavaBaseConstants.COLUMN_NAME_AB_META,
                                RedshiftDestinationConstants.SUPER_TYPE
                            ),
                            DSL.field<OffsetDateTime>(
                                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                                SQLDataType.TIMESTAMPWITHTIMEZONE
                            ),
                            DSL.field<OffsetDateTime>(
                                JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                                SQLDataType.TIMESTAMPWITHTIMEZONE
                            )
                        )
                    for (record in batch) {
                        insert =
                            insert.values(
                                DSL.`val`(UUID.randomUUID().toString()),
                                DSL.function(
                                    "JSON_PARSE",
                                    String::class.java,
                                    DSL.`val`(escapeStringLiteral(record.serialized))
                                ),
                                DSL.function(
                                    "JSON_PARSE",
                                    String::class.java,
                                    DSL.`val`(serialize(record.record!!.meta))
                                ),
                                DSL.`val`(
                                    Instant.ofEpochMilli(record.record!!.emittedAt)
                                        .atOffset(ZoneOffset.UTC)
                                ),
                                DSL.`val`(null as OffsetDateTime?)
                            )
                    }
                    val insertSQL = insert.getSQL(ParamType.INLINED)
                    LOGGER.info(
                        "Prepared batch size: {}, Schema: {}, Table: {}, SQL statement size {} MB",
                        batch.size,
                        schemaName,
                        tableName,
                        (insertSQL.toByteArray(StandardCharsets.UTF_8).size) / (1024 * 1024L)
                    )
                    val startTime = System.currentTimeMillis()
                    // Intentionally not using Jooq's insert.execute() as it was hiding the actual
                    // RedshiftException
                    // and also leaking the insert record values in the exception message.
                    connection.createStatement().execute(insertSQL)
                    LOGGER.info(
                        "Executed batch size: {}, Schema: {}, Table: {} in {} ms",
                        batch.size,
                        schemaName,
                        tableName,
                        (System.currentTimeMillis() - startTime)
                    )
                }
            }
        } catch (e: Exception) {
            LOGGER.error("Error while inserting records", e)
            throw RuntimeException(e)
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(RedshiftSqlOperations::class.java)
        const val REDSHIFT_VARCHAR_MAX_BYTE_SIZE: Int = 65535

        @JvmStatic
        fun escapeStringLiteral(str: String?): String? {
            return str?.replace("\\", "\\\\")
        }
    }
}
