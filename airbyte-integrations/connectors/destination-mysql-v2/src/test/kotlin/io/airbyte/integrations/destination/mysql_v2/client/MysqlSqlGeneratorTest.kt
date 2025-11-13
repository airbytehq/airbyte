/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.client

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.spec.SslMode
import io.airbyte.integrations.destination.mysql_v2.sql.MysqlColumnUtils
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class MysqlSqlGeneratorTest {

    private lateinit var columnUtils: MysqlColumnUtils
    private lateinit var config: MysqlConfiguration
    private lateinit var sqlGenerator: MysqlSqlGenerator

    @BeforeEach
    fun setup() {
        columnUtils = MysqlColumnUtils()
        config = MysqlConfiguration(
            host = "localhost",
            port = 3306,
            database = "test_db",
            username = "test_user",
            password = "test_pass",
            ssl = false,
            sslMode = SslMode.DISABLED,
            jdbcUrlParams = null,
            batchSize = 5000
        )
        sqlGenerator = MysqlSqlGenerator(columnUtils, config)
    }

    // ========== Namespace Tests ==========

    @Test
    fun testCreateNamespace() {
        val sql = sqlGenerator.createNamespace("test_namespace")
        assertEquals("CREATE DATABASE IF NOT EXISTS `test_namespace`", sql)
    }

    @Test
    fun testCreateNamespaceWithSpecialCharacters() {
        val sql = sqlGenerator.createNamespace("test-namespace")
        assertEquals("CREATE DATABASE IF NOT EXISTS `test-namespace`", sql)
    }

    @Test
    fun testNamespaceExists() {
        val sql = sqlGenerator.namespaceExists("test_namespace")
        assertTrue(sql.contains("SELECT SCHEMA_NAME"))
        assertTrue(sql.contains("FROM INFORMATION_SCHEMA.SCHEMATA"))
        assertTrue(sql.contains("WHERE SCHEMA_NAME = 'test_namespace'"))
    }

    // ========== Create Table Tests ==========

    @Test
    fun testCreateTableWithoutReplace() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true)
                )
            )
        )
        val tableName = TableName("test_db", "users")
        val columnMapping = ColumnNameMapping(mapOf("id" to "id", "name" to "name"))

        val sql = sqlGenerator.createTable(stream, tableName, columnMapping, replace = false)

        assertTrue(sql.contains("CREATE TABLE IF NOT EXISTS"))
        assertTrue(sql.contains("`test_db`.`users`"))
        assertTrue(sql.contains("`_airbyte_raw_id` VARCHAR(255) NOT NULL"))
        assertTrue(sql.contains("`_airbyte_extracted_at` TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)"))
        assertTrue(sql.contains("`_airbyte_meta` JSON NOT NULL"))
        assertTrue(sql.contains("`_airbyte_generation_id` BIGINT NOT NULL"))
        assertTrue(sql.contains("`id` BIGINT NOT NULL"))
        assertTrue(sql.contains("`name` TEXT"))
        assertTrue(sql.contains("PRIMARY KEY (`_airbyte_raw_id`)"))
    }

    @Test
    fun testCreateTableWithReplace() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, false)
                )
            )
        )
        val tableName = TableName("test_db", "users")
        val columnMapping = ColumnNameMapping(mapOf("id" to "id"))

        val sql = sqlGenerator.createTable(stream, tableName, columnMapping, replace = true)

        assertTrue(sql.contains("CREATE OR REPLACE TABLE IF NOT EXISTS"))
    }

    @Test
    fun testCreateTableFiltersAirbyteMetaColumns() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "_airbyte_raw_id" to FieldType(StringType, false),
                    "_airbyte_meta" to FieldType(StringType, false),
                    "user_id" to FieldType(IntegerType, false)
                )
            )
        )
        val tableName = TableName("test_db", "users")
        val columnMapping = ColumnNameMapping(
            mapOf(
                "_airbyte_raw_id" to "_airbyte_raw_id",
                "_airbyte_meta" to "_airbyte_meta",
                "user_id" to "user_id"
            )
        )

        val sql = sqlGenerator.createTable(stream, tableName, columnMapping, replace = false)

        // Should only have one `_airbyte_raw_id` declaration (the system one, not from schema)
        val count = sql.split("`_airbyte_raw_id`").size - 1
        assertEquals(2, count) // One in declaration, one in PRIMARY KEY
    }

    @Test
    fun testCreateTableWithVariousColumnTypes() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "timestamp_col" to FieldType(TimestampTypeWithTimezone, true),
                    "string_col" to FieldType(StringType, true),
                    "int_col" to FieldType(IntegerType, false)
                )
            )
        )
        val tableName = TableName("test_db", "events")
        val columnMapping = ColumnNameMapping(
            mapOf(
                "timestamp_col" to "timestamp_col",
                "string_col" to "string_col",
                "int_col" to "int_col"
            )
        )

        val sql = sqlGenerator.createTable(stream, tableName, columnMapping, replace = false)

        assertTrue(sql.contains("`timestamp_col` TIMESTAMP"))
        assertTrue(sql.contains("`string_col` TEXT"))
        assertTrue(sql.contains("`int_col` BIGINT NOT NULL"))
    }

    // ========== Drop Table Tests ==========

    @Test
    fun testDropTable() {
        val tableName = TableName("test_db", "users")
        val sql = sqlGenerator.dropTable(tableName)
        assertEquals("DROP TABLE IF EXISTS `test_db`.`users`", sql)
    }

    @Test
    fun testDropTableWithSpecialCharacters() {
        val tableName = TableName("test-db", "user-table")
        val sql = sqlGenerator.dropTable(tableName)
        assertEquals("DROP TABLE IF EXISTS `test-db`.`user-table`", sql)
    }

    // ========== Count Table Tests ==========

    @Test
    fun testCountTable() {
        val tableName = TableName("test_db", "users")
        val sql = sqlGenerator.countTable(tableName)
        assertTrue(sql.contains("SELECT COUNT(*) AS count"))
        assertTrue(sql.contains("FROM `test_db`.`users`"))
    }

    // ========== Get Generation ID Tests ==========

    @Test
    fun testGetGenerationId() {
        val tableName = TableName("test_db", "users")
        val sql = sqlGenerator.getGenerationId(tableName)
        assertTrue(sql.contains("SELECT `_airbyte_generation_id` AS generation_id"))
        assertTrue(sql.contains("FROM `test_db`.`users`"))
        assertTrue(sql.contains("LIMIT 1"))
    }

    // ========== Copy Table Tests ==========

    @Test
    fun testCopyTable() {
        val columnMapping = ColumnNameMapping(
            mapOf("id" to "id", "name" to "name", "email" to "email")
        )
        val source = TableName("test_db", "users_temp")
        val target = TableName("test_db", "users")

        val sql = sqlGenerator.copyTable(columnMapping, source, target)

        assertTrue(sql.contains("INSERT INTO `test_db`.`users`"))
        // Should include Airbyte metadata columns
        assertTrue(sql.contains("`_airbyte_raw_id`"))
        assertTrue(sql.contains("`_airbyte_extracted_at`"))
        assertTrue(sql.contains("`_airbyte_meta`"))
        assertTrue(sql.contains("`_airbyte_generation_id`"))
        // And user columns
        assertTrue(sql.contains("`id`"))
        assertTrue(sql.contains("`name`"))
        assertTrue(sql.contains("`email`"))
        assertTrue(sql.contains("FROM `test_db`.`users_temp`"))
    }

    @Test
    fun testCopyTableEmptyColumnMapping() {
        val columnMapping = ColumnNameMapping(emptyMap())
        val source = TableName("test_db", "source")
        val target = TableName("test_db", "target")

        val sql = sqlGenerator.copyTable(columnMapping, source, target)

        // Even with empty mapping, should include Airbyte columns
        assertTrue(sql.contains("INSERT INTO `test_db`.`target`"))
        assertTrue(sql.contains("`_airbyte_raw_id`"))
        assertTrue(sql.contains("SELECT"))
        assertTrue(sql.contains("FROM `test_db`.`source`"))
    }

    // ========== Overwrite Table Tests ==========

    @Test
    fun testOverwriteTable() {
        val source = TableName("test_db", "users_temp")
        val target = TableName("test_db", "users")

        val sqlList = sqlGenerator.overwriteTable(source, target)

        assertEquals(3, sqlList.size)

        // First statement: Rename target to backup
        assertTrue(sqlList[0].contains("RENAME TABLE `test_db`.`users` TO"))
        assertTrue(sqlList[0].contains("_airbyte_tmp_backup_"))

        // Second statement: Rename source to target
        assertTrue(sqlList[1].contains("RENAME TABLE `test_db`.`users_temp` TO `test_db`.`users`"))

        // Third statement: Drop backup
        assertTrue(sqlList[2].contains("DROP TABLE IF EXISTS"))
        assertTrue(sqlList[2].contains("_airbyte_tmp_backup_"))
    }

    @Test
    fun testOverwriteTableGeneratesUniqueBackupNames() {
        val source = TableName("test_db", "users_temp")
        val target = TableName("test_db", "users")

        val sqlList1 = sqlGenerator.overwriteTable(source, target)
        val sqlList2 = sqlGenerator.overwriteTable(source, target)

        // The backup table names should be different due to UUID
        assert(sqlList1[0] != sqlList2[0]) { "Backup table names should be unique" }
    }

    // ========== Upsert Table Tests ==========

    @Test
    fun testUpsertTableWithPrimaryKey() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true),
                    "email" to FieldType(StringType, true)
                )
            ),
            primaryKey = listOf(listOf("id")),
            cursor = listOf("updated_at")
        )
        val columnMapping = ColumnNameMapping(
            mapOf("id" to "id", "name" to "name", "email" to "email")
        )
        val source = TableName("test_db", "users_temp")
        val target = TableName("test_db", "users")

        val sqlList = sqlGenerator.upsertTable(stream, columnMapping, source, target)

        assertEquals(3, sqlList.size)

        // First statement: Create temp table with ROW_NUMBER deduplication
        assertTrue(sqlList[0].contains("CREATE TEMPORARY TABLE"))
        assertTrue(sqlList[0].contains("SELECT \* FROM"))
        assertTrue(sqlList[0].contains("ROW_NUMBER() OVER"))
        assertTrue(sqlList[0].contains("PARTITION BY `id`"))
        assertTrue(sqlList[0].contains("WHERE `row_number` = 1"))

        // Second statement: INSERT with ON DUPLICATE KEY UPDATE
        assertTrue(sqlList[1].contains("INSERT INTO `test_db`.`users`"))
        assertTrue(sqlList[1].contains("SELECT `id`, `name`, `email` FROM"))
        assertTrue(sqlList[1].contains("ON DUPLICATE KEY UPDATE"))
        assertTrue(sqlList[1].contains("`name` = VALUES(`name`)"))
        assertTrue(sqlList[1].contains("`email` = VALUES(`email`)"))

        // Third statement: DROP temp table
        assertTrue(sqlList[2].contains("DROP TEMPORARY TABLE"))
    }

    @Test
    fun testUpsertTableWithCompositePrimaryKey() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "tenant_id" to FieldType(IntegerType, false),
                    "user_id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true)
                )
            ),
            primaryKey = listOf(listOf("tenant_id"), listOf("user_id")),
            cursor = emptyList()
        )
        val columnMapping = ColumnNameMapping(
            mapOf("tenant_id" to "tenant_id", "user_id" to "user_id", "name" to "name")
        )
        val source = TableName("test_db", "users_temp")
        val target = TableName("test_db", "users")

        val sqlList = sqlGenerator.upsertTable(stream, columnMapping, source, target)

        assertEquals(3, sqlList.size)

        // First statement: Create temp table with composite PK partition
        assertTrue(sqlList[0].contains("CREATE TEMPORARY TABLE"))
        assertTrue(sqlList[0].contains("PARTITION BY `tenant_id`, `user_id`"))
        assertTrue(sqlList[0].contains("ORDER BY `_airbyte_extracted_at` DESC"))

        // Second statement: INSERT with ON DUPLICATE KEY UPDATE
        assertTrue(sqlList[1].contains("INSERT INTO"))
        assertTrue(sqlList[1].contains("ON DUPLICATE KEY UPDATE"))
        assertTrue(sqlList[1].contains("`name` = VALUES(`name`)"))
        assertTrue(!sqlList[1].contains("`tenant_id` = VALUES(`tenant_id`)"))
        assertTrue(!sqlList[1].contains("`user_id` = VALUES(`user_id`)"))

        // Third statement: DROP temp table
        assertTrue(sqlList[2].contains("DROP TEMPORARY TABLE"))
    }

    @Test
    fun testUpsertTableNoPrimaryKey() {
        val stream = mockDestinationStream(
            schema = ObjectType(
                properties = linkedMapOf(
                    "name" to FieldType(StringType, true),
                    "email" to FieldType(StringType, true)
                )
            ),
            primaryKey = emptyList(),
            cursor = emptyList(),
            forceDedupeType = true
        )
        val columnMapping = ColumnNameMapping(
            mapOf("name" to "name", "email" to "email")
        )
        val source = TableName("test_db", "users_temp")
        val target = TableName("test_db", "users")

        val sqlList = sqlGenerator.upsertTable(stream, columnMapping, source, target)

        assertEquals(3, sqlList.size)

        // First statement: Create temp table
        assertTrue(sqlList[0].contains("CREATE TEMPORARY TABLE"))

        // Second statement: INSERT IGNORE with DISTINCT in CTE (no PK)
        assertTrue(sqlList[1].contains("WITH deduped AS"))
        assertTrue(sqlList[1].contains("SELECT DISTINCT"))
        assertTrue(!sqlList[1].contains("ROW_NUMBER()"))

        // Without PK, should use INSERT IGNORE
        assertTrue(sqlList[1].contains("INSERT IGNORE INTO"))
        assertTrue(!sqlList[1].contains("ON DUPLICATE KEY UPDATE"))

        // Third statement: DROP temp table
        assertTrue(sqlList[2].contains("DROP TEMPORARY TABLE"))
    }

    @Test
    fun testUpsertTableThrowsExceptionForNonDedupeImportType() {
        val stream = mockk<DestinationStream> {
            every { importType } returns Append
            every { schema } returns ObjectType(
                properties = linkedMapOf(
                    "id" to FieldType(IntegerType, false)
                )
            )
        }
        val columnMapping = ColumnNameMapping(mapOf("id" to "id"))
        val source = TableName("test_db", "source")
        val target = TableName("test_db", "target")

        assertThrows(IllegalArgumentException::class.java) {
            sqlGenerator.upsertTable(stream, columnMapping, source, target)
        }
    }

    // ========== Alter Table Tests ==========

    @Test
    fun testAlterTableAddColumns() {
        val tableName = TableName("test_db", "users")
        val columnsToAdd = mapOf(
            "new_col1" to ColumnType("TEXT", true),
            "new_col2" to ColumnType("BIGINT", false)
        )

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = columnsToAdd,
            columnsToDrop = emptyMap(),
            columnsToChange = emptyMap()
        )

        assertEquals(2, sqlSet.size)
        assertTrue(sqlSet.any { it.contains("ALTER TABLE `test_db`.`users` ADD COLUMN `new_col1` TEXT") })
        assertTrue(sqlSet.any { it.contains("ALTER TABLE `test_db`.`users` ADD COLUMN `new_col2` BIGINT NOT NULL") })
    }

    @Test
    fun testAlterTableDropColumns() {
        val tableName = TableName("test_db", "users")
        val columnsToDrop = mapOf(
            "old_col1" to ColumnType("TEXT", true),
            "old_col2" to ColumnType("BIGINT", false)
        )

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = emptyMap(),
            columnsToDrop = columnsToDrop,
            columnsToChange = emptyMap()
        )

        assertEquals(2, sqlSet.size)
        assertTrue(sqlSet.any { it.contains("ALTER TABLE `test_db`.`users` DROP COLUMN `old_col1`") })
        assertTrue(sqlSet.any { it.contains("ALTER TABLE `test_db`.`users` DROP COLUMN `old_col2`") })
    }

    @Test
    fun testAlterTableModifyColumnNotNullToNull() {
        val tableName = TableName("test_db", "users")
        val columnsToChange = mapOf(
            "email" to ColumnTypeChange(
                originalType = ColumnType("TEXT", false),
                newType = ColumnType("TEXT", true)
            )
        )

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = emptyMap(),
            columnsToDrop = emptyMap(),
            columnsToChange = columnsToChange
        )

        assertEquals(1, sqlSet.size)
        assertTrue(sqlSet.any { it.contains("ALTER TABLE `test_db`.`users` MODIFY COLUMN `email` TEXT NULL") })
    }

    @Test
    fun testAlterTableModifyColumnTypeChange() {
        val tableName = TableName("test_db", "users")
        val columnsToChange = mapOf(
            "age" to ColumnTypeChange(
                originalType = ColumnType("INT", false),
                newType = ColumnType("BIGINT", false)
            )
        )

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = emptyMap(),
            columnsToDrop = emptyMap(),
            columnsToChange = columnsToChange
        )

        // Type change requires 4 statements: ADD temp, UPDATE data, DROP original, RENAME temp
        assertEquals(4, sqlSet.size)
        assertTrue(sqlSet.any { it.contains("ADD COLUMN") && it.contains("_tmp_") })
        assertTrue(sqlSet.any { it.contains("UPDATE") && it.contains("CAST") })
        assertTrue(sqlSet.any { it.contains("DROP COLUMN `age`") })
        assertTrue(sqlSet.any { it.contains("CHANGE COLUMN") && it.contains("`age` BIGINT") })
    }

    @Test
    fun testAlterTableModifyColumnNullToNotNullSkipped() {
        val tableName = TableName("test_db", "users")
        val columnsToChange = mapOf(
            "email" to ColumnTypeChange(
                originalType = ColumnType("TEXT", true),
                newType = ColumnType("TEXT", false)
            )
        )

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = emptyMap(),
            columnsToDrop = emptyMap(),
            columnsToChange = columnsToChange
        )

        // Should skip this unsafe change
        assertEquals(0, sqlSet.size)
    }

    @Test
    fun testAlterTableCombinedOperations() {
        val tableName = TableName("test_db", "users")
        val columnsToAdd = mapOf("new_col" to ColumnType("TEXT", true))
        val columnsToDrop = mapOf("old_col" to ColumnType("TEXT", true))
        val columnsToChange = mapOf(
            "existing_col" to ColumnTypeChange(
                originalType = ColumnType("VARCHAR(255)", false),
                newType = ColumnType("VARCHAR(255)", true)
            )
        )

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = columnsToAdd,
            columnsToDrop = columnsToDrop,
            columnsToChange = columnsToChange
        )

        // Should have: 1 ADD, 1 DROP, 1 MODIFY
        assertEquals(3, sqlSet.size)
        assertTrue(sqlSet.any { it.contains("ADD COLUMN") })
        assertTrue(sqlSet.any { it.contains("DROP COLUMN") })
        assertTrue(sqlSet.any { it.contains("MODIFY COLUMN") })
    }

    @Test
    fun testAlterTableEmptyOperations() {
        val tableName = TableName("test_db", "users")

        val sqlSet = sqlGenerator.alterTable(
            tableName = tableName,
            columnsToAdd = emptyMap(),
            columnsToDrop = emptyMap(),
            columnsToChange = emptyMap()
        )

        assertEquals(0, sqlSet.size)
    }

    // ========== Helper Methods ==========

    private fun mockDestinationStream(
        schema: ObjectType,
        primaryKey: List<List<String>> = emptyList(),
        cursor: List<String> = emptyList(),
        forceDedupeType: Boolean = false
    ): DestinationStream {
        val importType = if (primaryKey.isNotEmpty() || cursor.isNotEmpty() || forceDedupeType) {
            Dedupe(primaryKey = primaryKey, cursor = cursor)
        } else {
            Append
        }

        return mockk {
            every { this@mockk.schema } returns schema
            every { this@mockk.importType } returns importType
        }
    }
}
