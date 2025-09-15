/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

/**
 * Connector-specific stateless object which generates a valid [SelectQuery] for the corresponding
 * source database.
 *
 * This interface encapsulates the differences between all the SQL dialects out there.
 */
fun interface SelectQueryGenerator {
    fun generate(ast: SelectQuerySpec): SelectQuery
}
