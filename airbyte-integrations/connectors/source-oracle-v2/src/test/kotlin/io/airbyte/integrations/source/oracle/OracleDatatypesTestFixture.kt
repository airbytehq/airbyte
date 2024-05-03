/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons

/**
 * Reference: https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/Data-Types.html
 */
data object OracleDatatypesTestFixture {

    val testCases: List<TestCase> =
        listOf(
            // character datatypes
            TestCase("CHAR(10 BYTE)"),
            TestCase("CHAR(10 CHAR)"),
            TestCase("CHAR(10)"),
            TestCase("CHAR"),
            TestCase("VARCHAR2(10 BYTE)"),
            TestCase("VARCHAR2(10 CHAR)"),
            TestCase("VARCHAR2(10)"),
            TestCase("NCHAR(10)"),
            TestCase("NCHAR"),
            TestCase("NVARCHAR2(10)"),
            // number datatypes
            TestCase("NUMBER(10,2)"),
            TestCase("NUMBER(10)"),
            TestCase("NUMBER"),
            TestCase("FLOAT(10)"),
            TestCase("FLOAT"),
            TestCase("BINARY_FLOAT"),
            TestCase("BINARY_DOUBLE"),
            // long and raw datatypes
            TestCase("LONG", noPK = true, noVarray = true),
            TestCase("LONG RAW", noPK = true, noVarray = true),
            TestCase("RAW(10)"),
            // datetime datatypes
            TestCase("DATE"),
            TestCase("TIMESTAMP(2) WITH LOCAL TIME ZONE", noPK = true),
            TestCase("TIMESTAMP(2) WITH TIME ZONE", noPK = true),
            TestCase("TIMESTAMP(2)", noPK = true),
            TestCase("TIMESTAMP WITH LOCAL TIME ZONE", noPK = true),
            TestCase("TIMESTAMP WITH TIME ZONE", noPK = true),
            TestCase("TIMESTAMP", noPK = true),
            TestCase("INTERVAL YEAR(4) TO MONTH"),
            TestCase("INTERVAL YEAR TO MONTH"),
            TestCase("INTERVAL DAY(1) TO SECOND(2)"),
            TestCase("INTERVAL DAY(1) TO SECOND"),
            TestCase("INTERVAL DAY TO SECOND(2)"),
            TestCase("INTERVAL DAY TO SECOND"),
            // large object datatypes
            TestCase("BLOB", noPK = true, noVarray = true),
            TestCase("CLOB", noPK = true, noVarray = true),
            TestCase("NCLOB", noPK = true, noVarray = true),
            TestCase("BFILE", noPK = true),
            // rowid datatypes
            TestCase("ROWID", noVarray = true),
            TestCase("UROWID(100)", noVarray = true),
            TestCase("UROWID", noVarray = true),
            // json datatype
            TestCase("JSON", noPK = true, noVarray = true),
            // boolean datatype
            TestCase("BOOLEAN"),
            TestCase("BOOL"),
            // ANSI supported datatypes
            TestCase("CHARACTER VARYING (10)"),
            TestCase("CHARACTER (10)"),
            TestCase("CHAR VARYING (10)"),
            TestCase("NCHAR VARYING (10)"),
            TestCase("VARCHAR(10)"),
            TestCase("NATIONAL CHARACTER VARYING (10)"),
            TestCase("NATIONAL CHARACTER (10)"),
            TestCase("NATIONAL CHAR VARYING (10)"),
            TestCase("NATIONAL CHAR (10)"),
            TestCase("NUMERIC(10,2)"),
            TestCase("NUMERIC(10)"),
            TestCase("NUMERIC"),
            TestCase("DECIMAL(10,2)"),
            TestCase("DECIMAL(10)"),
            TestCase("DECIMAL"),
            TestCase("DEC(10,2)"),
            TestCase("DEC(10)"),
            TestCase("DEC"),
            TestCase("INTEGER"),
            TestCase("INT"),
            TestCase("SMALLINT", mapOf("1" to "1")),
            TestCase("FLOAT(10)"),
            TestCase("FLOAT"),
            TestCase("DOUBLE PRECISION"),
            TestCase("REAL"),
            // any types
            TestCase("SYS.AnyData", noPK = true, noVarray = true),
            TestCase("SYS.AnyType", noPK = true, noVarray = true),
            TestCase("SYS.AnyDataSet", noPK = true, noVarray = true),
            // xml types
            TestCase("XMLType", noPK = true, noVarray = true),
            TestCase("URItype", noPK = true),
            // spatial types
            TestCase("SDO_Geometry", noPK = true),
            TestCase("SDO_Topo_Geometry", noPK = true),
            // user-defined types
            TestCase(
                "fibo_objtyp",
                noPK = true,
                customDDL =
                    listOf(
                        """
    CREATE TYPE IF NOT EXISTS fibo_objtyp AS OBJECT (
        predecessor INTEGER, 
        n INTEGER,
        MEMBER FUNCTION getSuccessor RETURN INTEGER)""",
                        """
    CREATE TYPE BODY IF NOT EXISTS fibo_objtyp AS
        MEMBER FUNCTION getSuccessor RETURN INTEGER AS
        BEGIN
            RETURN predecessor + n;
        END getSuccessor;
    END""",
                        """
    CREATE TABLE IF NOT EXISTS tbl_fibo_objtyp (col_fibo_objtyp fibo_objtyp)""",
                        """
    CREATE TYPE IF NOT EXISTS varray_fibo_objtyp AS VARRAY(2) OF fibo_objtyp""",
                        """
    CREATE TABLE IF NOT EXISTS tbl_varray_fibo_objtyp (
        col_varray_fibo_objtyp varray_fibo_objtyp
    )""",
                        """
    TRUNCATE TABLE tbl_varray_fibo_objtyp CASCADE""",
                    )
            ),
            TestCase(
                "fibo_tbltyp",
                noPK = true,
                noVarray = true,
                customDDL =
                    listOf(
                        """
    CREATE TYPE IF NOT EXISTS fibo_tbltyp AS TABLE OF fibo_objtyp""",
                        """
    CREATE TABLE IF NOT EXISTS tbl_fibo_tbltyp (
        col_fibo_tbltyp fibo_tbltyp
    ) NESTED TABLE col_fibo_tbltyp STORE AS fibo_nt""",
                        """
    TRUNCATE TABLE tbl_fibo_tbltyp CASCADE"""
                    )
            ),
            TestCase(
                "REF fibo_objtyp",
                noPK = true,
                noVarray = true,
                customDDL =
                    listOf(
                        """
    CREATE TABLE IF NOT EXISTS fibo_ref_source OF fibo_objtyp""",
                        """
    CREATE TABLE IF NOT EXISTS tbl_fibo_tbltyp (
        col_ref_fibo_objtyp_scope_is_fibo_ref_source REF fibo_objtyp SCOPE IS fibo_ref_source
    )""",
                        """
    TRUNCATE TABLE tbl_fibo_tbltyp CASCADE""",
                    )
            ),
        )

    data class TestCase(
        val sqlType: String,
        val sqlToAirbyte: Map<String, String> = mapOf(),
        val noPK: Boolean = false,
        val noVarray: Boolean = false,
        val customDDL: List<String>? = null,
    ) {

        val id: String
            get() =
                sqlType
                    .replace("[^a-zA-Z0-9]".toRegex(), " ")
                    .trim()
                    .replace(" +".toRegex(), "_")
                    .lowercase()

        val tableName: String
            get() = "tbl_$id"

        val varraySqlType: String
            get() = "varray_$id"

        val varrayTableName: String
            get() = "tbl_varray_$id"

        val columnName: String
            get() = "col_$id"

        val varrayColumnName: String
            get() = "col_varray_$id"

        val sqlStatements: List<String>
            get() {
                val vanillaDDL: List<String> =
                    listOf(
                        "CREATE TABLE IF NOT EXISTS $tableName " +
                            "($columnName $sqlType ${if (noPK) "" else "PRIMARY KEY"})",
                        "TRUNCATE TABLE $tableName CASCADE"
                    )
                val vanillaDML: List<String> =
                    sqlToAirbyte.keys.map { "INSERT INTO $tableName ($columnName) VALUES (${it})" }
                val varrayDDL: List<String> =
                    listOf(
                        "CREATE TYPE IF NOT EXISTS $varraySqlType " + "AS VARRAY(2) OF $sqlType",
                        "CREATE TABLE IF NOT EXISTS $varrayTableName " +
                            "($varrayColumnName $varraySqlType)",
                        "TRUNCATE TABLE $varrayTableName"
                    )
                val varrayDML: List<String> =
                    sqlToAirbyte.keys.map {
                        "INSERT INTO $varrayTableName ($varrayColumnName) " +
                            "VALUES ($varraySqlType(${it}, ${it}))"
                    }
                val ddl: List<String> =
                    if (customDDL != null) {
                        customDDL
                    } else if (noVarray) {
                        vanillaDDL
                    } else {
                        vanillaDDL + varrayDDL
                    }
                val dml: List<String> =
                    if (noVarray) {
                        vanillaDML
                    } else {
                        vanillaDML + varrayDML
                    }
                return ddl + dml
            }

        val recordData: List<JsonNode>
            get() =
                sqlToAirbyte.values.toList().map { Jsons.deserialize("""{"$columnName":${it}}""") }

        val varrayRecordData: List<JsonNode>
            get() =
                sqlToAirbyte.values.toList().map {
                    Jsons.deserialize("""{"$varrayColumnName":[${it},${it}]}""")
                }
    }
}
