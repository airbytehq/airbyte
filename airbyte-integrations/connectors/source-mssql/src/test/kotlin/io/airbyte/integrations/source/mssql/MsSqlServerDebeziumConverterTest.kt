/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.mockk
import java.util.*
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MsSqlServerDebeziumConverterTest {

    private lateinit var converter: MsSqlServerDebeziumConverter

    @BeforeEach
    fun setUp() {
        converter = MsSqlServerDebeziumConverter()
    }

    @Test
    @DisplayName("Should load alias type mappings from properties")
    fun testConfigureLoadsAliasTypeMappings() {
        val properties = Properties()
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "MY_INT=INT,MY_VARCHAR=VARCHAR,MY_DATE=DATE"
        )

        converter.configure(properties)

        // Verify via converterFor: a column with alias type "MY_DATE" should be
        // resolved to "DATE" and get a converter registered (DATE type gets a converter)
        val field = mockRelationalColumn("test_col", "MY_DATE")
        val registration = TrackingConverterRegistration()
        converter.converterFor(field, registration)

        assertTrue(
            registration.wasRegistered,
            "Should register converter for alias type MY_DATE resolved to DATE"
        )
    }

    @Test
    @DisplayName("Should handle empty alias type mapping property")
    fun testConfigureWithEmptyMapping() {
        val properties = Properties()
        // No alias.type.mapping property set

        converter.configure(properties)

        // A standard type should still work
        val field = mockRelationalColumn("test_col", "DATE")
        val registration = TrackingConverterRegistration()
        converter.converterFor(field, registration)

        assertTrue(
            registration.wasRegistered,
            "Should still register converter for standard DATE type"
        )
    }

    @Test
    @DisplayName("Should resolve alias type to base type in converterFor")
    fun testConverterForResolvesAliasType() {
        val properties = Properties()
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "CUSTOM_MONEY=MONEY"
        )
        converter.configure(properties)

        val field = mockRelationalColumn("price_col", "custom_money")
        val registration = TrackingConverterRegistration()
        converter.converterFor(field, registration)

        assertTrue(
            registration.wasRegistered,
            "Should register converter for alias type CUSTOM_MONEY resolved to MONEY"
        )
    }

    @Test
    @DisplayName("Should not register converter for unknown alias types")
    fun testConverterForUnknownType() {
        val properties = Properties()
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "MY_INT=INT"
        )
        converter.configure(properties)

        // INT is not one of the special types that gets a converter registered
        // (only DATE, DATETIME, TIME, MONEY, BINARY, etc. get converters)
        val field = mockRelationalColumn("id_col", "MY_INT")
        val registration = TrackingConverterRegistration()
        converter.converterFor(field, registration)

        // INT falls through to the else branch (no converter registered)
        assertFalse(
            registration.wasRegistered,
            "Should not register converter for INT type (handled by default Debezium)"
        )
    }

    @Test
    @DisplayName("Should resolve multiple alias types correctly")
    fun testMultipleAliasTypes() {
        val properties = Properties()
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "MY_DATE=DATE,MY_MONEY=MONEY,MY_BINARY=BINARY,MY_TIME=TIME"
        )
        converter.configure(properties)

        // Test DATE alias
        val dateField = mockRelationalColumn("date_col", "MY_DATE")
        val dateReg = TrackingConverterRegistration()
        converter.converterFor(dateField, dateReg)
        assertTrue(dateReg.wasRegistered, "MY_DATE alias should resolve to DATE")

        // Test MONEY alias
        val moneyField = mockRelationalColumn("money_col", "MY_MONEY")
        val moneyReg = TrackingConverterRegistration()
        converter.converterFor(moneyField, moneyReg)
        assertTrue(moneyReg.wasRegistered, "MY_MONEY alias should resolve to MONEY")

        // Test BINARY alias
        val binaryField = mockRelationalColumn("binary_col", "MY_BINARY")
        val binaryReg = TrackingConverterRegistration()
        converter.converterFor(binaryField, binaryReg)
        assertTrue(binaryReg.wasRegistered, "MY_BINARY alias should resolve to BINARY")

        // Test TIME alias
        val timeField = mockRelationalColumn("time_col", "MY_TIME")
        val timeReg = TrackingConverterRegistration()
        converter.converterFor(timeField, timeReg)
        assertTrue(timeReg.wasRegistered, "MY_TIME alias should resolve to TIME")
    }

    @Test
    @DisplayName("Should handle case-insensitive alias type names")
    fun testCaseInsensitiveAliasNames() {
        val properties = Properties()
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "my_date=date"
        )
        converter.configure(properties)

        // Field reports type as mixed case
        val field = mockRelationalColumn("test_col", "My_Date")
        val registration = TrackingConverterRegistration()
        converter.converterFor(field, registration)

        assertTrue(
            registration.wasRegistered,
            "Should resolve alias type case-insensitively"
        )
    }

    @Test
    @DisplayName("Should handle malformed mapping entries gracefully")
    fun testMalformedMappingEntries() {
        val properties = Properties()
        // Mix of valid and invalid entries
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "GOOD_DATE=DATE,BAD_ENTRY,ALSO_BAD=,GOOD_MONEY=MONEY"
        )
        converter.configure(properties)

        // Valid entries should still work
        val dateField = mockRelationalColumn("date_col", "GOOD_DATE")
        val dateReg = TrackingConverterRegistration()
        converter.converterFor(dateField, dateReg)
        assertTrue(dateReg.wasRegistered, "Valid DATE alias should work despite malformed entries")

        val moneyField = mockRelationalColumn("money_col", "GOOD_MONEY")
        val moneyReg = TrackingConverterRegistration()
        converter.converterFor(moneyField, moneyReg)
        assertTrue(moneyReg.wasRegistered, "Valid MONEY alias should work despite malformed entries")
    }

    @Test
    @DisplayName("Standard types should still work without alias resolution")
    fun testStandardTypesUnaffected() {
        val properties = Properties()
        properties.setProperty(
            MsSqlServerDebeziumConverter.ALIAS_TYPE_MAPPING_PROPERTY,
            "MY_CUSTOM=DATE"
        )
        converter.configure(properties)

        // Standard DATE type should still work directly
        val field = mockRelationalColumn("std_date", "DATE")
        val registration = TrackingConverterRegistration()
        converter.converterFor(field, registration)
        assertTrue(registration.wasRegistered, "Standard DATE type should still get a converter")
    }

    private fun mockRelationalColumn(name: String, typeName: String): RelationalColumn {
        val column = mockk<RelationalColumn>()
        every { column.name() } returns name
        every { column.typeName() } returns typeName
        return column
    }

    /**
     * Tracks whether a converter was registered via the registration callback.
     */
    private class TrackingConverterRegistration :
        CustomConverter.ConverterRegistration<SchemaBuilder> {
        var wasRegistered = false

        override fun register(
            fieldSchema: SchemaBuilder,
            converter: CustomConverter.Converter
        ) {
            wasRegistered = true
        }
    }
}
