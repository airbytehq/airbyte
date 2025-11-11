/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeSqlNameUtilsTest {

    private lateinit var snowflakeConfiguration: SnowflakeConfiguration
    private lateinit var snowflakeSqlNameUtils: SnowflakeSqlNameUtils

    @BeforeEach
    fun setUp() {
        snowflakeConfiguration = mockk(relaxed = true)
        snowflakeSqlNameUtils =
            SnowflakeSqlNameUtils(snowflakeConfiguration = snowflakeConfiguration)
    }

    @Test
    fun testFullyQualifiedName() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        val name = "test=name"
        val tableName = TableName(namespace = namespace, name = name)
        every { snowflakeConfiguration.database } returns databaseName

        val expectedName =
            snowflakeSqlNameUtils.combineParts(
                listOf(
                    databaseName.toSnowflakeCompatibleName(),
                    tableName.namespace,
                    tableName.name
                )
            )
        val fullyQualifiedName = snowflakeSqlNameUtils.fullyQualifiedName(tableName)
        assertEquals(expectedName, fullyQualifiedName)
    }

    @Test
    fun testFullyQualifiedNamespace() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        every { snowflakeConfiguration.database } returns databaseName

        val fullyQualifiedNamespace = snowflakeSqlNameUtils.fullyQualifiedNamespace(namespace)
        assertEquals("\"TEST-DATABASE\".\"test-namespace\"", fullyQualifiedNamespace)
    }

    @Test
    fun testFullyQualifiedStageName() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        val name = "test=name"
        val tableName = TableName(namespace = namespace, name = name)
        every { snowflakeConfiguration.database } returns databaseName

        val expectedName =
            snowflakeSqlNameUtils.combineParts(
                listOf(
                    databaseName.toSnowflakeCompatibleName(),
                    namespace,
                    "$STAGE_NAME_PREFIX$name"
                )
            )
        val fullyQualifiedName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        assertEquals(expectedName, fullyQualifiedName)
    }

    @Test
    fun testFullyQualifiedStageNameWithEscape() {
        val databaseName = "test-database"
        val namespace = "test-namespace"
        val name = "test=\"\"\'name"
        val tableName = TableName(namespace = namespace, name = name)
        every { snowflakeConfiguration.database } returns databaseName

        val expectedName =
            snowflakeSqlNameUtils.combineParts(
                listOf(
                    databaseName.toSnowflakeCompatibleName(),
                    namespace,
                    "$STAGE_NAME_PREFIX${sqlEscape(name)}"
                )
            )
        val fullyQualifiedName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName, true)
        assertEquals(expectedName, fullyQualifiedName)
    }
}
