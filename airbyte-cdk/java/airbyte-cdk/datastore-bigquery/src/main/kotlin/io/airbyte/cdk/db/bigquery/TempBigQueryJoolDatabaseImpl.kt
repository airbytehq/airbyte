/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.bigquery

import io.airbyte.cdk.db.ContextQueryFunction
import io.airbyte.cdk.db.Database
import java.sql.SQLException
import java.util.*
import org.jooq.Record
import org.jooq.Result
import org.jooq.SQLDialect
import org.jooq.exception.DataAccessException
import org.jooq.impl.DefaultDSLContext

/** This class is a temporary and will be removed as part of the issue @TODO #4547 */
class TempBigQueryJoolDatabaseImpl(
    projectId: String?,
    jsonCreds: String?,
    realDatabase: BigQueryDatabase = createBigQueryDatabase(projectId, jsonCreds)
) : Database(FakeDefaultDSLContext(realDatabase)) {

    @Throws(SQLException::class)
    override fun <T> query(transform: ContextQueryFunction<T>): T? {
        return transform.query(dslContext)
    }

    @Throws(SQLException::class)
    override fun <T> transaction(transform: ContextQueryFunction<T>): T? {
        return transform.query(dslContext)
    }

    private class FakeDefaultDSLContext(private val database: BigQueryDatabase) :
        DefaultDSLContext(null as SQLDialect?) {
        @Throws(DataAccessException::class)
        override fun fetch(sql: String): Result<Record> {
            try {
                database.execute(sql)
            } catch (e: SQLException) {
                throw DataAccessException(e.message, e)
            }
            return fetchFromStringData(Collections.emptyList())
        }
    }

    companion object {
        fun createBigQueryDatabase(projectId: String?, jsonCreds: String?): BigQueryDatabase {
            return BigQueryDatabase(projectId, jsonCreds)
        }
    }
}
