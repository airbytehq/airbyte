/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.ResultSetMetaData
import java.sql.SQLException
import java.sql.Statement
import java.sql.Types
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers.any
import org.mockito.ArgumentMatchers.anyString
import org.mockito.ArgumentMatchers.contains
import org.mockito.Mockito.mock
import org.mockito.Mockito.times
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`

/**
 * Unit tests for the discover tolerance behavior of [SnowflakeSourceMetadataQuerier].
 *
 * These exercise the [SnowflakeSourceMetadataQuerier.fields] ->
 * [SnowflakeSourceMetadataQuerier.columnMetadata] -> queryColumnMetadata path against a mocked
 * JDBC [Connection]. The tests cover each tolerated vendor error code and SQLSTATE, the
 * unknown-is-fatal default, per-column fallback, and operation gating.
 */
class SnowflakeSourceMetadataQuerierTest {

    companion object {
        private const val DATABASE = "TESTDB"
        private const val SCHEMA = "PUBLIC"
        private const val GOOD_VIEW = "GOOD_VIEW"
        private const val BAD_VIEW = "BAD_VIEW"

        // View compilation/expansion failures -> tolerable, whole-object.
        private const val SQLSTATE_COMPILE_ERROR = "42601"
        private const val ERRORCODE_VIEW_DECLARED_MISMATCH = 2057
        private const val ERRORCODE_VIEW_EXPANSION_FAILURE = 2037

        // Object does not exist or is not authorized -> tolerable, whole-object when paired
        // with vendor codes 2003 or 2043.
        private const val SQLSTATE_NO_DATA = "02000"
        private const val ERRORCODE_OBJECT_NOT_FOUND = 2003
        private const val ERRORCODE_OBJECT_UNAUTHORIZED = 2043

        // Insufficient privilege -> tolerable, but NOT whole-object.
        private const val SQLSTATE_ACCESS_DENIED = "42501"

        // --- Fatal failures ---

        //NETWORK_ERROR/IO_ERROR
        private const val SQLSTATE_DRIVER_NETWORK = "58030"
        private const val ERRORCODE_DRIVER_NETWORK = 200015

        // Auth/session token expiry: driver reauthentication codes
        private const val SQLSTATE_INTERNAL = "XX000"
        private const val ERRORCODE_TOKEN_EXPIRED = 390114

        // "No active warehouse selected"
        private const val SQLSTATE_NO_WAREHOUSE = "57P03"
        private const val ERRORCODE_NO_WAREHOUSE = 401

        private const val PROBE_ALL_COLUMNS = "\"ID\", \"ID2\""
        private const val PROBE_ID_ONLY = "SELECT \"ID\" FROM \"$SCHEMA\".\"$BAD_VIEW\""
        private const val PROBE_ID2_ONLY = "SELECT \"ID2\" FROM"
    }

    /** Holds the querier under test and mocked [Statement] for interaction verification. */
    private class Fixture(val querier: SnowflakeSourceMetadataQuerier, val stmt: Statement)

    /** Builds a [SnowflakeSourceMetadataQuerier] whose base delegates to the given [Connection]. */
    private fun querierFor(
        conn: Connection,
        tolerateObjectLevelFailures: Boolean,
        checkPrivileges: Boolean,
    ): SnowflakeSourceMetadataQuerier {
        val ops = SnowflakeSourceOperations()
        val config =
            SnowflakeSourceConfiguration(
                realHost = "localhost",
                jdbcUrlFmt = "jdbc:snowflake://%s",
                jdbcProperties = emptyMap(),
                namespaces = setOf(DATABASE),
                schema = SCHEMA,
                incremental = UserDefinedCursorIncrementalConfiguration,
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofSeconds(60),
                checkPrivileges = checkPrivileges,
            )

        val connectionFactory = mock(JdbcConnectionFactory::class.java)
        `when`(connectionFactory.get()).thenReturn(conn)
        val base =
            JdbcMetadataQuerier(
                constants = DefaultJdbcConstants(),
                config = config,
                selectQueryGenerator = ops,
                fieldTypeMapper = ops,
                checkQueries = JdbcCheckQueries(),
                jdbcConnectionFactory = connectionFactory,
            )
        return SnowflakeSourceMetadataQuerier(base, SCHEMA, tolerateObjectLevelFailures)
    }

    /** A mocked [ResultSet] over [DatabaseMetaData.getTables] enumerating two views. */
    private fun tablesResultSet(): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(true, true, false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(DATABASE, DATABASE)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(SCHEMA, SCHEMA)
        `when`(rs.getString("TABLE_NAME")).thenReturn(GOOD_VIEW, BAD_VIEW)
        `when`(rs.getString("TABLE_TYPE")).thenReturn("VIEW", "VIEW")
        return rs
    }

    /** A mocked [ResultSet] over [DatabaseMetaData.getColumns] with one column per view. */
    private fun columnsResultSet(): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(true, true, false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(DATABASE, DATABASE)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(SCHEMA, SCHEMA)
        `when`(rs.getString("TABLE_NAME")).thenReturn(GOOD_VIEW, BAD_VIEW)
        `when`(rs.getString("COLUMN_NAME")).thenReturn("ID", "ID")
        `when`(rs.getString("TYPE_NAME")).thenReturn("NUMBER", "NUMBER")
        `when`(rs.getInt("DATA_TYPE")).thenReturn(Types.NUMERIC, Types.NUMERIC)
        `when`(rs.getInt("COLUMN_SIZE")).thenReturn(38, 38)
        `when`(rs.getInt("DECIMAL_DIGITS")).thenReturn(0, 0)
        `when`(rs.getInt("ORDINAL_POSITION")).thenReturn(1, 1)
        `when`(rs.getString("IS_NULLABLE")).thenReturn("YES", "YES")
        `when`(rs.wasNull()).thenReturn(false)
        return rs
    }

    /** Like [columnsResultSet], but BAD_VIEW has two columns: ID and ID2. */
    private fun twoColumnBadViewColumnsResultSet(): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(true, true, true, false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(DATABASE, DATABASE, DATABASE)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(SCHEMA, SCHEMA, SCHEMA)
        `when`(rs.getString("TABLE_NAME")).thenReturn(GOOD_VIEW, BAD_VIEW, BAD_VIEW)
        // once for `name` and once for `label`
        `when`(rs.getString("COLUMN_NAME")).thenReturn("ID", "ID", "ID", "ID", "ID2", "ID2")
        `when`(rs.getString("TYPE_NAME")).thenReturn("NUMBER", "NUMBER", "NUMBER")
        `when`(rs.getInt("DATA_TYPE")).thenReturn(Types.NUMERIC, Types.NUMERIC, Types.NUMERIC)
        `when`(rs.getInt("COLUMN_SIZE")).thenReturn(38, 38, 38)
        `when`(rs.getInt("DECIMAL_DIGITS")).thenReturn(0, 0, 0)
        `when`(rs.getInt("ORDINAL_POSITION")).thenReturn(1, 1, 2)
        `when`(rs.getString("IS_NULLABLE")).thenReturn("YES", "YES", "YES")
        `when`(rs.wasNull()).thenReturn(false)
        return rs
    }

    /** A successful single-column LIMIT 0 probe result set (metadata only). */
    private fun probeResultSet(columnName: String = "ID"): ResultSet {
        val meta = mock(ResultSetMetaData::class.java)
        `when`(meta.columnCount).thenReturn(1)
        `when`(meta.getColumnName(1)).thenReturn(columnName)
        `when`(meta.getColumnLabel(1)).thenReturn(columnName)
        `when`(meta.getColumnTypeName(1)).thenReturn("NUMBER")
        `when`(meta.getColumnType(1)).thenReturn(Types.NUMERIC)
        `when`(meta.getPrecision(1)).thenReturn(38)
        `when`(meta.getScale(1)).thenReturn(0)
        `when`(meta.isNullable(1)).thenReturn(ResultSetMetaData.columnNullable)
        val rs = mock(ResultSet::class.java)
        `when`(rs.metaData).thenReturn(meta)
        return rs
    }

    /**
     * Wires a mocked [Connection] whose metadata enumerates GOOD_VIEW + BAD_VIEW, and whose LIMIT-0
     * probe succeeds for GOOD_VIEW but throws [probeFailure] for BAD_VIEW.
     */
    private fun fixtureWith(
        probeFailure: SQLException,
        tolerateObjectLevelFailures: Boolean = true,
        checkPrivileges: Boolean = true,
    ): Fixture {
        val dbmd = mock(DatabaseMetaData::class.java)
        `when`(dbmd.getTables(anyString(), any(), any(), any())).thenAnswer { tablesResultSet() }
        `when`(dbmd.getColumns(any(), any(), any(), any())).thenAnswer { columnsResultSet() }

        val stmt = mock(Statement::class.java)
        `when`(stmt.executeQuery(contains(BAD_VIEW))).thenThrow(probeFailure)
        `when`(stmt.executeQuery(contains(GOOD_VIEW))).thenAnswer { probeResultSet() }

        val conn = mock(Connection::class.java)
        `when`(conn.metaData).thenReturn(dbmd)
        `when`(conn.createStatement()).thenReturn(stmt)
        return Fixture(querierFor(conn, tolerateObjectLevelFailures, checkPrivileges), stmt)
    }

    /**
     * Like [fixtureWith], but BAD_VIEW has two columns (ID, ID2): the all-columns probe throws
     * [allColumnsFailure], the single-ID probe throws [idColumnFailure], and the single-ID2 probe
     * succeeds.
     */
    private fun twoColumnBadViewFixture(
        allColumnsFailure: SQLException,
        idColumnFailure: SQLException,
    ): Fixture {
        val dbmd = mock(DatabaseMetaData::class.java)
        `when`(dbmd.getTables(anyString(), any(), any(), any())).thenAnswer { tablesResultSet() }
        `when`(dbmd.getColumns(any(), any(), any(), any())).thenAnswer {
            twoColumnBadViewColumnsResultSet()
        }

        val stmt = mock(Statement::class.java)
        `when`(stmt.executeQuery(contains(GOOD_VIEW))).thenAnswer { probeResultSet() }
        `when`(stmt.executeQuery(contains(PROBE_ALL_COLUMNS))).thenThrow(allColumnsFailure)
        `when`(stmt.executeQuery(contains(PROBE_ID_ONLY))).thenThrow(idColumnFailure)
        `when`(stmt.executeQuery(contains(PROBE_ID2_ONLY))).thenAnswer { probeResultSet("ID2") }

        val conn = mock(Connection::class.java)
        `when`(conn.metaData).thenReturn(dbmd)
        `when`(conn.createStatement()).thenReturn(stmt)
        return Fixture(querierFor(conn, tolerateObjectLevelFailures = true, checkPrivileges = true), stmt)
    }

    private fun streamId(name: String): StreamIdentifier =
        StreamIdentifier.from(StreamDescriptor().withName(name).withNamespace(SCHEMA))

    private fun assertHardDiscoveryFailure(fixture: Fixture, view: String) {
        val e =
            assertThrows(RuntimeException::class.java) { fixture.querier.fields(streamId(view)) }
        assertTrue(
            e.message?.contains("Column name discovery query failed") == true,
            "Expected a hard discovery failure, got: ${e.message}",
        )
    }

    // --- Tolerated object-level failures (discover mode) ---
    @Test
    fun `invalid view is skipped while healthy streams still discover`() {
        val fixture =
            fixtureWith(
                SQLException(
                    "invalid view",
                    SQLSTATE_COMPILE_ERROR,
                    ERRORCODE_VIEW_DECLARED_MISMATCH,
                ),
            )

        // Healthy view
        val goodFields = fixture.querier.fields(streamId(GOOD_VIEW))
        assertEquals(1, goodFields.size)
        assertEquals("ID", goodFields.single().id)

        // Broken view - yields NO fields instead of failing the whole discover
        val badFields = fixture.querier.fields(streamId(BAD_VIEW))
        assertTrue(badFields.isEmpty())
    }

    @Test
    fun `whole-object compile failure short-circuits the per-column probes`() {
        val fixture =
            fixtureWith(
                SQLException(
                    "invalid view",
                    SQLSTATE_COMPILE_ERROR,
                    ERRORCODE_VIEW_DECLARED_MISMATCH,
                ),
            )

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
        // Whole-object failures should not fall back to per-column probes.
        verify(fixture.stmt, times(1)).executeQuery(contains(BAD_VIEW))
    }

    @Test
    fun `view column-drift vendor code short-circuits probes even with a null sqlState`() {
        // Pins the errorCode-2057 branch of both the allowlist and the whole-object check,
        // independently of SQLSTATE 42601.
        val fixture =
            fixtureWith(SQLException("invalid view", null, ERRORCODE_VIEW_DECLARED_MISMATCH))

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
        verify(fixture.stmt, times(1)).executeQuery(contains(BAD_VIEW))
    }

    @Test
    fun `view-expansion compile error short-circuits probes via sqlState alone`() {
        val fixture =
            fixtureWith(
                SQLException(
                    "Failure during expansion of view 'BAD_VIEW'",
                    SQLSTATE_COMPILE_ERROR,
                    ERRORCODE_VIEW_EXPANSION_FAILURE,
                ),
            )

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
        verify(fixture.stmt, times(1)).executeQuery(contains(BAD_VIEW))
    }

    @Test
    fun `access-denial sqlState falls back to per-column probing and keeps accessible columns`() {
        // Pins the SQLSTATE 42501 tolerance branch and the per-column fallback:
        // the all-columns probe fails, ID is inaccessible, and only ID2 is kept.
        val fixture =
            twoColumnBadViewFixture(
                allColumnsFailure = SQLException("access denied", SQLSTATE_ACCESS_DENIED, 0),
                idColumnFailure = SQLException("access denied", SQLSTATE_ACCESS_DENIED, 0),
            )

        assertEquals(listOf("ID2"), fixture.querier.fields(streamId(BAD_VIEW)).map { it.id })

        // Three distinct probes: all-columns, then one per column.
        verify(fixture.stmt, times(1)).executeQuery(contains(PROBE_ALL_COLUMNS))
        verify(fixture.stmt, times(1)).executeQuery(contains(PROBE_ID_ONLY))
        verify(fixture.stmt, times(1)).executeQuery(contains(PROBE_ID2_ONLY))
    }

    @Test
    fun `object-not-found vendor code is tolerated even with a null sqlState`() {
        // Pins the errorCode branch of the allowlist independently of SQLSTATE.
        val fixture =
            fixtureWith(
                SQLException("does not exist or not authorized", null, ERRORCODE_OBJECT_NOT_FOUND)
            )

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
        verify(fixture.stmt, times(1)).executeQuery(contains(BAD_VIEW))
    }

    @Test
    fun `object-unauthorized vendor code is tolerated even with a null sqlState`() {
        // Pins the errorCode-2043 allowlist entry on its own, proves the probe ran and short-circuited.
        val fixture =
            fixtureWith(
                SQLException(
                    "does not exist or not authorized",
                    null,
                    ERRORCODE_OBJECT_UNAUTHORIZED,
                )
            )

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
        verify(fixture.stmt, times(1)).executeQuery(contains(BAD_VIEW))
    }

    @Test
    fun `no-data sqlState is tolerated independently of the vendor code`() {
        // Pins the SQLSTATE 02000 tolerance path with an unlisted errorCode.
        val fixture = fixtureWith(SQLException("object not visible", SQLSTATE_NO_DATA, 0))

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
        verify(fixture.stmt, times(2)).executeQuery(contains(BAD_VIEW))
    }

    // --- checkPrivileges guard: probes only run when privilege checking is enabled ---
    @Test
    fun `disabled privilege checks return catalog metadata without probing`() {
        // Pins the checkPrivileges guard: with probes off, even a broken view keeps its
        // catalog-metadata columns and no LIMIT-0 query ever runs.
        val fixture =
            fixtureWith(SQLException("mystery failure", null, 999999), checkPrivileges = false)

        assertEquals(listOf("ID"), fixture.querier.fields(streamId(BAD_VIEW)).map { it.id })
        verify(fixture.stmt, times(0)).executeQuery(anyString())
    }

    // --- Fatal failures: NOT object-level, must propagate even in discover mode ---
    @Test
    fun `driver network failure propagates as a hard error`() {
        // snowflake-jdbc surfaces network/IO failures as SQLSTATE 58030 (class '58', not '08').
        // Tolerating it would silently truncate the catalog for every remaining stream.
        val fixture =
            fixtureWith(
                SQLException("network error", SQLSTATE_DRIVER_NETWORK, ERRORCODE_DRIVER_NETWORK),
            )

        assertHardDiscoveryFailure(fixture, BAD_VIEW)
    }

    @Test
    fun `expired auth token propagates as a hard error`() {
        // Driver reauthentication codes (e.g. PAT/session token expiry) default to SQLSTATE XX000.
        val fixture =
            fixtureWith(SQLException("token expired", SQLSTATE_INTERNAL, ERRORCODE_TOKEN_EXPIRED))

        assertHardDiscoveryFailure(fixture, BAD_VIEW)
    }

    @Test
    fun `no active warehouse propagates as a hard error`() {
        val fixture =
            fixtureWith(
                SQLException(
                    "No active warehouse selected",
                    SQLSTATE_NO_WAREHOUSE,
                    ERRORCODE_NO_WAREHOUSE,
                ),
            )

        assertHardDiscoveryFailure(fixture, BAD_VIEW)
    }

    @Test
    fun `unknown failure with no sqlState propagates as a hard error`() {
        // Pins the unknown-is-fatal default: not in the allowlist -> loud failure, never a
        // silently truncated catalog.
        val fixture = fixtureWith(SQLException("mystery failure", null, 999999))

        assertHardDiscoveryFailure(fixture, BAD_VIEW)
    }

    // --- Operation gating: tolerance is discover-only ---
    @Test
    fun `tolerance disabled - object-level failure propagates as before`() {
        // CHECK relies on a throwing fields() to detect roles that cannot SELECT anything, and READ
        // must fail loudly on a broken selected stream.
        val fixture =
            fixtureWith(
                SQLException(
                    "invalid view",
                    SQLSTATE_COMPILE_ERROR,
                    ERRORCODE_VIEW_DECLARED_MISMATCH,
                ),
                tolerateObjectLevelFailures = false,
            )

        assertHardDiscoveryFailure(fixture, BAD_VIEW)
    }
}
