/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata.util

import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/** Unit tests for the JSONStruct class. */
class JSONStructTest {

    private lateinit var struct: JSONStruct
    private val json: String = "{\n" + "\t\"id\":123,\n" + "\t\"name\":\"Pankaj Kumar\",\n" + "}"

    /** Setup method to initialize objects before each test. */
    @BeforeEach
    fun setup() {
        struct = JSONStruct("JSON", arrayOf<Any?>(json))
    }

    /**
     * Test the getAttributes method.
     *
     * @throws SQLException if an SQL exception occurs
     */
    @Test
    @Throws(SQLException::class)
    fun testGetAttributes() {
        Assertions.assertEquals(json, struct.attributes[0])
    }

    /**
     * Test the getSQLTypeName method.
     *
     * @throws SQLException if an SQL exception occurs
     */
    @Test
    @Throws(SQLException::class)
    fun testGetSQLTypeName() {
        Assertions.assertEquals("JSON", struct.sqlTypeName)
    }
}
