/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.ConfigErrorException
import java.sql.SQLException

object MSSQLErrorClassifier {
    // SQL Server error numbers, see sys.messages:
    //   229 - permission denied on an object (e.g. INSERT on a table)
    //   230 - permission denied on a column
    //   262 - permission denied in the database (e.g. CREATE TABLE)
    //   297 - user does not have permission to perform this action
    private val PERMISSION_DENIED_ERROR_CODES = setOf(229, 230, 262, 297)
    //   2628 - string or binary data would be truncated in table/column (SQL Server 2019+)
    //   8152 - string or binary data would be truncated (legacy message)
    private val STRING_TRUNCATION_ERROR_CODES = setOf(2628, 8152)

    /**
     * Rethrows [e] as a ConfigErrorException when it is a known user-fixable SQL Server error,
     * otherwise rethrows it unchanged.
     */
    fun rethrowClassified(e: SQLException): Nothing {
        val chain = generateSequence<Throwable>(e) { it.cause }.toList()
        val codes = chain.filterIsInstance<SQLException>().map { it.errorCode }
        val messages = chain.mapNotNull { it.message }
        when {
            codes.any { it in PERMISSION_DENIED_ERROR_CODES } ||
                messages.any { it.contains("permission was denied", ignoreCase = true) } ->
                throw ConfigErrorException(
                    "Database user lacks permission on the destination table.",
                    e
                )
            codes.any { it in STRING_TRUNCATION_ERROR_CODES } ||
                messages.any { it.contains("would be truncated", ignoreCase = true) } ->
                throw ConfigErrorException(
                    "Record value exceeds the length of a destination table column.",
                    e
                )
            else -> throw e
        }
    }
}
