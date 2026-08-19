/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.sql

import io.airbyte.cdk.load.schema.model.TableName
import jakarta.inject.Singleton

internal const val QUOTE: String = "\""

/**
 * Surrounds the string instance with double quotation marks. Redshift uses PostgreSQL-style double
 * quotes for identifiers.
 */
fun String.quote() = "$QUOTE$this$QUOTE"

@Singleton
class RedshiftSqlNameUtils {

    fun fullyQualifiedName(tableName: TableName): String =
        "${tableName.namespace.quote()}.${tableName.name.quote()}"

    fun fullyQualifiedNamespace(namespace: String): String = namespace.quote()
}
