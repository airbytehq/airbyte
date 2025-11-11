/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.cdk.db.jdbc.JdbcDatabase

interface JdbcGenerationHandler {
    /**
     * get the value of _airbyte_generation_id for any row in table {@code rawNamespace.rawName}
     *
     * @returns true if the table exists and contains such a row, false otherwise
     */
    fun getGenerationIdInTable(database: JdbcDatabase, namespace: String, name: String): Long?
}
