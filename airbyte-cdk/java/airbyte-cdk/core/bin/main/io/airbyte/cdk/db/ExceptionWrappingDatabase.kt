/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import java.io.*
import java.sql.SQLException

/** Wraps a [Database] object and throwing IOExceptions instead of SQLExceptions. */
class ExceptionWrappingDatabase(private val database: Database) {
    @Throws(IOException::class)
    fun <T> query(transform: ContextQueryFunction<T>): T? {
        try {
            return database.query(transform)
        } catch (e: SQLException) {
            throw IOException(e)
        }
    }

    @Throws(IOException::class)
    fun <T> transaction(transform: ContextQueryFunction<T>): T? {
        try {
            return database.transaction(transform)
        } catch (e: SQLException) {
            throw IOException(e)
        }
    }
}
