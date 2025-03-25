/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.util

import java.sql.SQLException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/** Class representing a JSONStruct. */
class JSONStruct(private val sqlTypeName: String, private val attributes: Array<Any>) {

    /** Returns the attributes. */
    fun getAttributes(): Array<Any> {
        return attributes
    }

    /**
     * Returns the attributes using the provided map.
     *
     * @param map A map of attribute names to their classes.
     * @throws SQLException always thrown with a specific message.
     */
    @Throws(SQLException::class)
    fun getAttributes(map: Map<String, Class<*>>): Array<Any> {
        throw SQLException("getAttributes (Map) NOT SUPPORTED")
    }

    /**
     * Returns the SQL type name.
     *
     * @throws SQLException if an SQL exception occurs.
     */
    @Throws(SQLException::class)
    fun getSQLTypeName(): String {
        return sqlTypeName
    }
}

/** Unit tests for the JSONStruct class. */
class JSONStructTest {

    private lateinit var struct: JSONStruct
    private val json: String = "{\n" + "\t\"id\":123,\n" + "\t\"name\":\"Pankaj Kumar\",\n" + "}"

    /** Setup method to initialize objects before each test. */
    @BeforeEach
    fun setup() {
        struct = JSONStruct("JSON", arrayOf(json))
    }

    /**
     * Test the getAttributes method.
     *
     * @throws SQLException if an SQL exception occurs
     */
    @Test
    @Throws(SQLException::class)
    fun testGetAttributes() {
        assertEquals(json, struct.getAttributes()[0])
    }

    /** Test the getAttributes method when an exception is expected. */
    @Test
    fun testGetAttributesException() {
        val exception =
            assertThrows(SQLException::class.java) {
                val inputMap: MutableMap<String, Class<*>> = HashMap()
                struct.getAttributes(inputMap)
            }
        val expectedMessage = "getAttributes (Map) NOT SUPPORTED"
        val actualMessage = exception.message
        assertTrue(actualMessage!!.contains(expectedMessage))
    }

    /**
     * Test the getSQLTypeName method.
     *
     * @throws SQLException if an SQL exception occurs
     */
    @Test
    @Throws(SQLException::class)
    fun testGetSQLTypeName() {
        assertEquals("JSON", struct.getSQLTypeName())
    }
}
