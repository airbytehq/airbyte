/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata.util

import java.sql.SQLException
import java.sql.Struct

/**
 * Utility class to handle Teradata JSON data type. The JSON data type stores text as a CLOB in
 * either CHARACTER SET LATIN or CHARACTER SET UNICODE. A JSON value sent to the Teradata database
 * using a Struct containing String or a Reader attribute.
 */
class JSONStruct
/**
 * Constructs a new JSONStruct with the specified SQL type name and attributes.
 *
 * @param sqlTypeName The SQL type name.
 * @param attributes The attributes of the JSONStruct.
 */
(private val m_sqlTypeName: String, private val m_attributes: Array<Any>) : Struct {
    /**
     * Retrieves the attributes of this JSONStruct.
     *
     * @return An array containing the attributes of this JSONStruct.
     * @throws SQLException if a database access error occurs.
     */
    @Throws(SQLException::class)
    override fun getAttributes(): Array<Any> {
        return m_attributes
    }

    /**
     * Retrieves the SQL type name of this JSONStruct.
     *
     * @return The SQL type name of this JSONStruct.
     * @throws SQLException if a database access error occurs.
     */
    @Throws(SQLException::class)
    override fun getSQLTypeName(): String {
        return m_sqlTypeName
    }

    // This method is not supported, but needs to be included
    /**
     * Retrieves the attributes of this JSONStruct with the specified map.
     *
     * @param map A map containing the attributes.
     * @return An array containing the attributes of this JSONStruct.
     * @throws SQLException if a database access error occurs.
     */
    @Throws(SQLException::class)
    override fun getAttributes(p0: MutableMap<String, Class<*>>?): Array<Any> {
        throw SQLException("getAttributes (Map) NOT SUPPORTED")
    }
}
