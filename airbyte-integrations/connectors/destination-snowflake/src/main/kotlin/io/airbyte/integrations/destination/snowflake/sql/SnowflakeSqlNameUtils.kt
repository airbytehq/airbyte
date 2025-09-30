/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton

const val STAGE_NAME_PREFIX = "airbyte_stage_"
internal const val STAGE_FORMAT_NAME: String = "airbyte_csv_format"
internal const val QUOTE: String = "\""

@Singleton
class SnowflakeSqlNameUtils(
    private val snowflakeConfiguration: SnowflakeConfiguration,
) {
    fun escape(part: String) = part.replace("'", "\\'").replace("\"", "\\\"")

    fun fullyQualifiedName(tableName: TableName): String =
        combineParts(listOf(getDatabaseName(), tableName.namespace, tableName.name))

    fun fullyQualifiedNamespace(namespace: String) =
        combineParts(listOf(getDatabaseName(), namespace))

    fun fullyQualifiedStageName(tableName: TableName, escape: Boolean = false): String =
        combineParts(
            parts =
                listOf(
                    getDatabaseName(),
                    tableName.namespace,
                    "$STAGE_NAME_PREFIX${tableName.name}"
                ),
            escape = escape,
        )

    fun fullyQualifiedFormatName(namespace: String): String =
        combineParts(listOf(getDatabaseName(), namespace, STAGE_FORMAT_NAME))

    fun combineParts(parts: List<String>, escape: Boolean = false): String =
        parts
            .map {
                val compatible = it.toSnowflakeCompatibleName()
                if (escape) escape(compatible) else compatible
            }
            .joinToString(separator = ".") {
                if (!it.startsWith(QUOTE)) {
                    "$QUOTE$it$QUOTE"
                } else {
                    it
                }
            }

    private fun getDatabaseName() = snowflakeConfiguration.database
}
