/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

import io.airbyte.cdk.ConfigErrorException
import io.mockk.confirmVerified
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.spyk
import io.mockk.verify
import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.SortOrder
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties.DEFAULT_FILE_FORMAT
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Type.PrimitiveType
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/**
 * Tests for [IcebergTableSynchronizer].
 *
 * We use a mocked [Table] and [UpdateSchema] to verify that the right calls are made based on the
 * computed [IcebergTypesComparator.ColumnDiff].
 */
class IcebergTableSynchronizerTest {

    // Mocks
    private lateinit var mockTable: Table
    private lateinit var mockUpdateSchema: UpdateSchema
    private lateinit var mockNewSchema: Schema

    // Collaborators under test
    private val comparator = spyk(IcebergTypesComparator())
    private val superTypeFinder = spyk(IcebergSuperTypeFinder(comparator))
    private val synchronizer = IcebergTableSynchronizer(comparator, superTypeFinder)

    @BeforeEach
    fun setUp() {
        // Prepare the mocks before each test
        mockTable = mockk(relaxed = true)
        mockUpdateSchema = mockk(relaxed = true)
        mockNewSchema = mockk(relaxed = true)

        // By default, let table.schema() return an empty schema. Tests can override this as needed.
        every { mockTable.schema() } returns Schema(listOf())

        // By default, the table has no sort order. Tests using real tables handle this themselves.
        every { mockTable.sortOrder() } returns SortOrder.unsorted()

        // Table.updateSchema() should return the mock UpdateSchema
        every { mockTable.updateSchema().allowIncompatibleChanges() } returns mockUpdateSchema

        // apply should return a fake schema
        every { mockUpdateSchema.apply() } returns mockNewSchema

        // No-op for the commit call unless specifically tested for. We'll verify calls later.
        every { mockUpdateSchema.commit() } just runs
    }

    /** Helper to build a schema with [Types.NestedField]s. */
    private fun buildSchema(
        vararg fields: Types.NestedField,
        identifierFields: Set<Int> = emptySet()
    ): Schema {
        return Schema(fields.toList(), identifierFields)
    }

    @Test
    fun `test no changes - should do nothing`() {
        // The existing schema is the same as incoming => no diffs
        val existingSchema =
            buildSchema(Types.NestedField.required(1, "id", Types.IntegerType.get()))
        existingSchema.identifierFieldNames()
        val incomingSchema =
            buildSchema(Types.NestedField.required(1, "id", Types.IntegerType.get()))

        every { mockTable.schema() } returns existingSchema
        // The comparator will see no changes
        every { comparator.compareSchemas(incomingSchema, existingSchema) } answers
            {
                IcebergTypesComparator.ColumnDiff()
            }

        val result =
            synchronizer.maybeApplySchemaChanges(
                mockTable,
                incomingSchema,
                ColumnTypeChangeBehavior.SAFE_SUPERTYPE
            )

        // We expect the original schema to be returned
        assertThat(result)
            .isEqualTo(SchemaUpdateResult(existingSchema, pendingUpdates = emptyList()))

        // Verify that no calls to updateSchema() manipulation were made
        verify(exactly = 0) { mockUpdateSchema.deleteColumn(any()) }
        verify(exactly = 0) { mockUpdateSchema.updateColumn(any(), any<PrimitiveType>()) }
        verify(exactly = 0) { mockUpdateSchema.makeColumnOptional(any()) }
        verify(exactly = 0) { mockUpdateSchema.addColumn(any<String>(), any<String>(), any()) }
        verify(exactly = 0) { mockUpdateSchema.setIdentifierFields(any<Collection<String>>()) }
        verify(exactly = 0) { mockUpdateSchema.commit() }
        verify(exactly = 0) { mockTable.refresh() }
    }

    @Test
    fun `test remove columns`() {
        val existingSchema =
            buildSchema(Types.NestedField.optional(1, "remove_me", Types.StringType.get()))
        val incomingSchema = buildSchema() // empty => remove everything

        every { mockTable.schema() } returns existingSchema

        val result =
            synchronizer.maybeApplySchemaChanges(
                mockTable,
                incomingSchema,
                ColumnTypeChangeBehavior.SAFE_SUPERTYPE
            )

        // The result is a new schema after changes, but we can only verify calls on the mock
        // Here we expect remove_me to be deleted.
        verify { mockUpdateSchema.deleteColumn("remove_me") }
        verify { mockUpdateSchema.commit() }

        // The final returned schema is the table's schema after refresh
        // Since we aren't actually applying changes, just assert that it's whatever the mock
        // returns
        assertThat(result)
            .isEqualTo(SchemaUpdateResult(mockNewSchema, pendingUpdates = emptyList()))
    }

    @Test
    fun `test update data type to supertype`() {
        val existingSchema =
            buildSchema(Types.NestedField.optional(2, "age", Types.IntegerType.get()))
        val incomingSchema = buildSchema(Types.NestedField.optional(2, "age", Types.LongType.get()))

        every { mockTable.schema() } returns existingSchema

        // Apply changes
        synchronizer.maybeApplySchemaChanges(
            mockTable,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        )

        // Verify that "age" is updated to LONG
        verify { mockUpdateSchema.updateColumn("age", Types.LongType.get()) }
        // And that changes are committed
        verify { mockUpdateSchema.commit() }
    }

    @Test
    fun `test newly optional columns`() {
        val existingSchema =
            buildSchema(Types.NestedField.required(3, "make_optional", Types.StringType.get()))
        val incomingSchema =
            buildSchema(Types.NestedField.optional(3, "make_optional", Types.StringType.get()))

        every { mockTable.schema() } returns existingSchema

        synchronizer.maybeApplySchemaChanges(
            mockTable,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        )

        // We expect makeColumnOptional("make_optional") to be called
        verify { mockUpdateSchema.makeColumnOptional("make_optional") }
        verify { mockUpdateSchema.commit() }
    }

    @Test
    fun `test add new columns - top level`() {
        val existingSchema =
            buildSchema(Types.NestedField.required(1, "id", Types.IntegerType.get()))
        val incomingSchema =
            buildSchema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "new_col", Types.StringType.get()),
            )

        every { mockTable.schema() } returns existingSchema

        synchronizer.maybeApplySchemaChanges(
            mockTable,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        )

        verify { mockUpdateSchema.addColumn(null, "new_col", Types.StringType.get()) }
        verify { mockUpdateSchema.commit() }
    }

    @Test
    fun `test add new columns - nested one-level`() {
        val existingSchema =
            buildSchema(
                Types.NestedField.required(
                    1,
                    "user_info",
                    Types.StructType.of(
                        Types.NestedField.required(2, "nested_id", Types.IntegerType.get())
                    )
                )
            )
        val incomingSchema =
            buildSchema(
                Types.NestedField.required(
                    1,
                    "user_info",
                    Types.StructType.of(
                        Types.NestedField.required(2, "nested_id", Types.IntegerType.get()),
                        // new subfield
                        Types.NestedField.optional(3, "nested_name", Types.StringType.get()),
                    )
                )
            )

        every { mockTable.schema() } returns existingSchema

        // For the newly added leaf "nested_name"
        // We'll also ensure that the subfield is found
        val userInfoStruct = incomingSchema.findField("user_info")!!.type().asStructType()
        val nestedNameField = userInfoStruct.asSchema().findField("nested_name")
        assertThat(nestedNameField).isNotNull // Just a sanity check in the test

        synchronizer.maybeApplySchemaChanges(
            mockTable,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        )

        verify { mockUpdateSchema.addColumn("user_info", "nested_name", Types.StringType.get()) }
        verify { mockUpdateSchema.commit() }
    }

    @Test
    fun `test add new columns - more than one-level nesting throws`() {
        // e.g. "outer~inner~leaf" is two levels
        val existingSchema = buildSchema()
        val incomingSchema = buildSchema() // Not too relevant, since we expect an exception

        every { mockTable.schema() } returns existingSchema
        val diff = IcebergTypesComparator.ColumnDiff(newColumns = mutableListOf("outer~inner~leaf"))
        every { comparator.compareSchemas(incomingSchema, existingSchema) } returns diff

        assertThatThrownBy {
                synchronizer.maybeApplySchemaChanges(
                    mockTable,
                    incomingSchema,
                    ColumnTypeChangeBehavior.SAFE_SUPERTYPE
                )
            }
            .isInstanceOf(ConfigErrorException::class.java)
            .hasMessageContaining("Adding nested columns more than 1 level deep is not supported")

        // No calls to commit
        verify(exactly = 0) { mockUpdateSchema.commit() }
        verify(exactly = 0) { mockTable.refresh() }
    }

    @Test
    fun `test update with non-primitive supertype throws`() {
        // Suppose the comparator says that "complex_col" has an updated data type
        // but the superTypeFinder returns a struct (non-primitive).
        val existingSchema =
            buildSchema(Types.NestedField.required(10, "complex_col", Types.StructType.of()))
        val incomingSchema =
            buildSchema(Types.NestedField.required(10, "complex_col", Types.StructType.of()))

        every { mockTable.schema() } returns existingSchema
        val diff =
            IcebergTypesComparator.ColumnDiff(updatedDataTypes = mutableListOf("complex_col"))
        every { comparator.compareSchemas(incomingSchema, existingSchema) } returns diff

        // Let superTypeFinder return a struct type
        val structType =
            Types.StructType.of(Types.NestedField.optional(1, "field", Types.StringType.get()))
        every { superTypeFinder.findSuperType(any(), any(), "complex_col") } returns structType

        assertThatThrownBy {
                synchronizer.maybeApplySchemaChanges(
                    mockTable,
                    incomingSchema,
                    ColumnTypeChangeBehavior.SAFE_SUPERTYPE
                )
            }
            .isInstanceOf(ConfigErrorException::class.java)
            .hasMessageContaining("Currently only primitive type updates are supported.")

        // No updates or commits
        verify(exactly = 0) { mockUpdateSchema.updateColumn(any(), any<PrimitiveType>()) }
        verify(exactly = 0) { mockUpdateSchema.commit() }
        verify(exactly = 0) { mockTable.refresh() }
    }

    @Test
    fun `test update identifier fields`() {
        val existingSchema =
            buildSchema(Types.NestedField.required(3, "id", Types.StringType.get()))
        val incomingSchema =
            buildSchema(
                Types.NestedField.required(3, "id", Types.StringType.get()),
                identifierFields = setOf(3)
            )

        every { mockTable.schema() } returns existingSchema

        synchronizer.maybeApplySchemaChanges(
            mockTable,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        )

        // We expect setIdentifierFields(listOf("id")) to be called
        verify { mockUpdateSchema.requireColumn("id") }
        verify { mockUpdateSchema.setIdentifierFields(listOf("id")) }
        verify { mockUpdateSchema.commit() }
    }

    @Test
    fun `test multiple operations in one pass`() {
        val existingSchema =
            buildSchema(
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                Types.NestedField.optional(2, "remove_me", Types.StringType.get()),
                Types.NestedField.required(3, "make_optional", Types.IntegerType.get()),
                Types.NestedField.required(4, "upgrade_int", Types.IntegerType.get())
            )
        val incomingSchema =
            buildSchema(
                // "remove_me" is gone -> removal
                Types.NestedField.required(1, "id", Types.IntegerType.get()),
                // make_optional -> newly optional
                Types.NestedField.optional(3, "make_optional", Types.IntegerType.get()),
                // upgrade_int -> changed to long
                Types.NestedField.required(4, "upgrade_int", Types.LongType.get()),
                // brand_new -> new column
                Types.NestedField.optional(5, "brand_new", Types.FloatType.get()),
                identifierFields = setOf(1)
            )

        every { mockTable.schema() } returns existingSchema

        // Suppose superTypeFinder says int->long is valid
        every {
            superTypeFinder.findSuperType(
                Types.IntegerType.get(),
                Types.LongType.get(),
                "upgrade_int"
            )
        } returns Types.LongType.get()

        synchronizer.maybeApplySchemaChanges(
            mockTable,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE
        )

        // Verify calls, in any order
        verify { mockUpdateSchema.deleteColumn("remove_me") }
        verify { mockUpdateSchema.updateColumn("upgrade_int", Types.LongType.get()) }
        verify { mockUpdateSchema.makeColumnOptional("make_optional") }
        verify { mockUpdateSchema.addColumn(null, "brand_new", Types.FloatType.get()) }
        verify { mockUpdateSchema.requireColumn("id") }
        verify { mockUpdateSchema.setIdentifierFields(listOf("id")) }

        verify { mockUpdateSchema.commit() }
    }

    @Test
    fun `test fail on incompatible type change`() {
        val existingSchema =
            buildSchema(Types.NestedField.optional(2, "age", Types.IntegerType.get()))
        val incomingSchema =
            buildSchema(Types.NestedField.optional(2, "age", Types.StringType.get()))

        every { mockTable.schema() } returns existingSchema

        assertThatThrownBy {
                synchronizer.maybeApplySchemaChanges(
                    mockTable,
                    incomingSchema,
                    ColumnTypeChangeBehavior.SAFE_SUPERTYPE
                )
            }
            .isInstanceOf(ConfigErrorException::class.java)
            .hasMessage(
                """Schema evolution for column "age" between int and string is not allowed."""
            )
    }

    @Test
    fun `test overwrite on incompatible type change`() {
        val existingSchema =
            buildSchema(Types.NestedField.optional(2, "age", Types.IntegerType.get()))
        val incomingSchema =
            buildSchema(Types.NestedField.optional(2, "age", Types.StringType.get()))

        every { mockTable.schema() } returns existingSchema

        val (schema, pendingUpdates) =
            synchronizer.maybeApplySchemaChanges(
                mockTable,
                incomingSchema,
                ColumnTypeChangeBehavior.OVERWRITE
            )

        verify { mockUpdateSchema.deleteColumn("age") }
        verify { mockUpdateSchema.addColumn("age", Types.StringType.get()) }
        verify(exactly = 0) { mockUpdateSchema.commit() }
        // reminder: apply() doesn't actually make any changes, it just verifies
        // that the schema change is valid
        verify { mockUpdateSchema.apply() }
        confirmVerified(mockUpdateSchema)

        assertThat(schema).isSameAs(mockNewSchema)
        assertThat(pendingUpdates).hasSize(1)
    }

    @Test
    fun `test overwrite with replaced column as identifier field defers identifier update`() {
        // Simulates the scenario where a PK column's type changes (e.g. Double -> String)
        // and the column is also an identifier field. Iceberg's requireColumn() fails for
        // columns pending deletion, so we must commit the column replacement first, then
        // handle identifier fields in a follow-up update.
        val existingSchema =
            buildSchema(Types.NestedField.required(1, "pk_col", Types.DoubleType.get()))
        val incomingSchema =
            buildSchema(
                Types.NestedField.required(1, "pk_col", Types.StringType.get()),
                identifierFields = setOf(1)
            )

        every { mockTable.schema() } returns existingSchema

        // After the first commit (column replacement), table.updateSchema() returns a new mock
        val mockIdentifierUpdateSchema = mockk<UpdateSchema>(relaxed = true)
        val mockIdentifierNewSchema = mockk<Schema>(relaxed = true)
        every { mockIdentifierUpdateSchema.apply() } returns mockIdentifierNewSchema

        // First call returns mockUpdateSchema, second call (after commit+refresh) returns
        // the identifier update mock.
        every { mockTable.updateSchema().allowIncompatibleChanges() } returnsMany
            listOf(mockUpdateSchema, mockIdentifierUpdateSchema)

        val (schema, pendingUpdates) =
            synchronizer.maybeApplySchemaChanges(
                mockTable,
                incomingSchema,
                ColumnTypeChangeBehavior.OVERWRITE
            )

        // First update: delete + add column (committed immediately due to deferred identifiers)
        verify { mockUpdateSchema.deleteColumn("pk_col") }
        verify { mockUpdateSchema.addColumn("pk_col", Types.StringType.get()) }
        verify { mockUpdateSchema.commit() }

        // Table is refreshed after the first commit
        verify { mockTable.refresh() }

        // Second update: identifier fields handled in a follow-up
        verify { mockIdentifierUpdateSchema.requireColumn("pk_col") }
        verify { mockIdentifierUpdateSchema.setIdentifierFields(listOf("pk_col")) }
        // OVERWRITE mode doesn't commit immediately — returns as pending
        verify(exactly = 0) { mockIdentifierUpdateSchema.commit() }

        assertThat(schema).isSameAs(mockIdentifierNewSchema)
        assertThat(pendingUpdates).hasSize(1)
        assertThat(pendingUpdates.first()).isSameAs(mockIdentifierUpdateSchema)
    }

    // ==================================================================================
    // Sort order tests — use real HadoopCatalog tables (not mocks) because mocked tests
    // never exercise Iceberg's SortOrder.checkCompatibility validation.
    // ==================================================================================

    private fun createRealSynchronizer() =
        IcebergTableSynchronizer(
            IcebergTypesComparator(),
            IcebergSuperTypeFinder(IcebergTypesComparator()),
        )

    /** Schema matching the customer's custom insight streams (Dedupe with 3 PKs). */
    private fun dedupeSchema() =
        Schema(
            listOf(
                Types.NestedField.required(1, "_airbyte_raw_id", Types.StringType.get()),
                Types.NestedField.required(
                    2,
                    "_airbyte_extracted_at",
                    Types.TimestampType.withZone()
                ),
                Types.NestedField.required(3, "_airbyte_meta", Types.StringType.get()),
                Types.NestedField.required(4, "_airbyte_generation_id", Types.LongType.get()),
                Types.NestedField.required(5, "ad_id", Types.StringType.get()),
                Types.NestedField.required(6, "date_start", Types.DateType.get()),
                Types.NestedField.required(7, "account_id", Types.StringType.get()),
                Types.NestedField.optional(8, "impressions", Types.LongType.get()),
            ),
            setOf(5, 6, 7), // identifier fields: ad_id, date_start, account_id
        )

    private fun dedupeSortOrder(schema: Schema): SortOrder =
        SortOrder.builderFor(schema).asc("ad_id").asc("date_start").asc("account_id").build()

    private fun createTableWithSortOrder(
        catalog: HadoopCatalog,
        tableId: TableIdentifier,
        schema: Schema,
        sortOrder: SortOrder,
    ): Table {
        catalog.createNamespace(tableId.namespace())
        return catalog
            .buildTable(tableId, schema)
            .withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
            .withSortOrder(sortOrder)
            .create()
    }

    private fun createTableWithoutSortOrder(
        catalog: HadoopCatalog,
        tableId: TableIdentifier,
        schema: Schema,
    ): Table {
        catalog.createNamespace(tableId.namespace())
        return catalog
            .buildTable(tableId, schema)
            .withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
            .create()
    }

    /**
     * Scenario A: Source upgrade removes a PK column (ad_id) that the sort order references. After
     * fix: schema evolution should succeed and sort order should retain only the remaining PK
     * columns.
     */
    @Test
    fun `scenario A - removing a sort-order column should update sort order and succeed`() {
        val warehousePath = Files.createTempDirectory("iceberg-test-warehouse")
        val catalog = HadoopCatalog(Configuration(), warehousePath.toString())
        val tableId = TableIdentifier.of("db", "scenario_a")

        val schema = dedupeSchema()
        val table = createTableWithSortOrder(catalog, tableId, schema, dedupeSortOrder(schema))

        // Incoming schema: ad_id removed, identifiers updated
        val incomingSchema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "_airbyte_raw_id", Types.StringType.get()),
                    Types.NestedField.required(
                        2,
                        "_airbyte_extracted_at",
                        Types.TimestampType.withZone()
                    ),
                    Types.NestedField.required(3, "_airbyte_meta", Types.StringType.get()),
                    Types.NestedField.required(4, "_airbyte_generation_id", Types.LongType.get()),
                    // ad_id (field 5) removed
                    Types.NestedField.required(6, "date_start", Types.DateType.get()),
                    Types.NestedField.required(7, "account_id", Types.StringType.get()),
                    Types.NestedField.optional(8, "impressions", Types.LongType.get()),
                ),
                setOf(6, 7), // identifier fields: date_start, account_id
            )

        val synchronizer = createRealSynchronizer()
        synchronizer.maybeApplySchemaChanges(
            table,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
        )

        // ad_id should be gone from the schema
        table.refresh()
        assertThat(table.schema().findField("ad_id")).isNull()

        // Sort order should have 2 remaining fields (date_start, account_id)
        val updatedSortOrder = table.sortOrder()
        assertThat(updatedSortOrder.fields()).hasSize(2)
        assertThat(updatedSortOrder.fields().map { table.schema().findColumnName(it.sourceId()) })
            .containsExactly("date_start", "account_id")

        catalog.dropTable(tableId)
        warehousePath.toFile().deleteRecursively()
    }

    /**
     * Scenario B: Stream switches from Dedupe to Append. Incoming schema has no identifier fields.
     * The sort order should be cleared to unsorted.
     */
    @Test
    fun `scenario B - dedupe to append should clear sort order`() {
        val warehousePath = Files.createTempDirectory("iceberg-test-warehouse")
        val catalog = HadoopCatalog(Configuration(), warehousePath.toString())
        val tableId = TableIdentifier.of("db", "scenario_b")

        val schema = dedupeSchema()
        val table = createTableWithSortOrder(catalog, tableId, schema, dedupeSortOrder(schema))

        // Incoming schema: same columns but NO identifier fields (Append mode)
        val incomingSchema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "_airbyte_raw_id", Types.StringType.get()),
                    Types.NestedField.required(
                        2,
                        "_airbyte_extracted_at",
                        Types.TimestampType.withZone()
                    ),
                    Types.NestedField.required(3, "_airbyte_meta", Types.StringType.get()),
                    Types.NestedField.required(4, "_airbyte_generation_id", Types.LongType.get()),
                    Types.NestedField.optional(5, "ad_id", Types.StringType.get()),
                    Types.NestedField.optional(6, "date_start", Types.DateType.get()),
                    Types.NestedField.optional(7, "account_id", Types.StringType.get()),
                    Types.NestedField.optional(8, "impressions", Types.LongType.get()),
                ),
                // No identifier fields — Append mode
                )

        val synchronizer = createRealSynchronizer()
        synchronizer.maybeApplySchemaChanges(
            table,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
        )

        table.refresh()
        assertThat(table.sortOrder().isUnsorted).isTrue()

        catalog.dropTable(tableId)
        warehousePath.toFile().deleteRecursively()
    }

    /**
     * Scenario D (with column deletion): PKs change within Dedupe and the old PK column is also
     * removed from the schema. Sort order should be updated to match new PKs, and the column
     * deletion should succeed.
     *
     * This is the exact customer scenario: ad_id removed from both PKs and schema.
     */
    @Test
    fun `scenario D - pk change with column deletion should update sort order`() {
        val warehousePath = Files.createTempDirectory("iceberg-test-warehouse")
        val catalog = HadoopCatalog(Configuration(), warehousePath.toString())
        val tableId = TableIdentifier.of("db", "scenario_d_with_delete")

        val schema = dedupeSchema()
        val table = createTableWithSortOrder(catalog, tableId, schema, dedupeSortOrder(schema))

        // Incoming schema: ad_id removed from both columns and identifiers
        val incomingSchema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "_airbyte_raw_id", Types.StringType.get()),
                    Types.NestedField.required(
                        2,
                        "_airbyte_extracted_at",
                        Types.TimestampType.withZone()
                    ),
                    Types.NestedField.required(3, "_airbyte_meta", Types.StringType.get()),
                    Types.NestedField.required(4, "_airbyte_generation_id", Types.LongType.get()),
                    // ad_id removed
                    Types.NestedField.required(6, "date_start", Types.DateType.get()),
                    Types.NestedField.required(7, "account_id", Types.StringType.get()),
                    Types.NestedField.optional(8, "impressions", Types.LongType.get()),
                ),
                setOf(6, 7), // identifier fields: date_start, account_id
            )

        val synchronizer = createRealSynchronizer()
        synchronizer.maybeApplySchemaChanges(
            table,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
        )

        table.refresh()
        assertThat(table.schema().findField("ad_id")).isNull()

        val updatedSortOrder = table.sortOrder()
        assertThat(updatedSortOrder.fields()).hasSize(2)
        assertThat(updatedSortOrder.fields().map { table.schema().findColumnName(it.sourceId()) })
            .containsExactly("date_start", "account_id")

        catalog.dropTable(tableId)
        warehousePath.toFile().deleteRecursively()
    }

    /**
     * Scenario D (standalone): PKs change within Dedupe but the old PK column remains in the schema
     * as a non-PK column. Sort order should be updated to match new PKs.
     */
    @Test
    fun `scenario D - pk change without column deletion should update sort order`() {
        val warehousePath = Files.createTempDirectory("iceberg-test-warehouse")
        val catalog = HadoopCatalog(Configuration(), warehousePath.toString())
        val tableId = TableIdentifier.of("db", "scenario_d_standalone")

        val schema = dedupeSchema()
        val table = createTableWithSortOrder(catalog, tableId, schema, dedupeSortOrder(schema))

        // Incoming schema: ad_id still present but no longer an identifier
        val incomingSchema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "_airbyte_raw_id", Types.StringType.get()),
                    Types.NestedField.required(
                        2,
                        "_airbyte_extracted_at",
                        Types.TimestampType.withZone()
                    ),
                    Types.NestedField.required(3, "_airbyte_meta", Types.StringType.get()),
                    Types.NestedField.required(4, "_airbyte_generation_id", Types.LongType.get()),
                    Types.NestedField.optional(5, "ad_id", Types.StringType.get()),
                    Types.NestedField.required(6, "date_start", Types.DateType.get()),
                    Types.NestedField.required(7, "account_id", Types.StringType.get()),
                    Types.NestedField.optional(8, "impressions", Types.LongType.get()),
                ),
                setOf(6, 7), // identifier fields: date_start, account_id (ad_id removed from PKs)
            )

        val synchronizer = createRealSynchronizer()
        synchronizer.maybeApplySchemaChanges(
            table,
            incomingSchema,
            ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
        )

        table.refresh()
        // ad_id should still exist as a column
        assertThat(table.schema().findField("ad_id")).isNotNull()

        // Sort order should reflect new PKs only
        val updatedSortOrder = table.sortOrder()
        assertThat(updatedSortOrder.fields()).hasSize(2)
        assertThat(updatedSortOrder.fields().map { table.schema().findColumnName(it.sourceId()) })
            .containsExactly("date_start", "account_id")

        catalog.dropTable(tableId)
        warehousePath.toFile().deleteRecursively()
    }
}
