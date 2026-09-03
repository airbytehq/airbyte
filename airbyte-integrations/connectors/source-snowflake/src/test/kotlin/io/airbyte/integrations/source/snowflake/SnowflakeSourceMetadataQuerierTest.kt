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
 * These exercise the real [fields] -> [SnowflakeSourceMetadataQuerier.columnMetadata] ->
 * queryColumnMetadata path against a mocked JDBC [Connection]. The tolerance classification is an
 * ALLOWLIST of object-level errors, so each suite below pins one branch of the classifier: a test
 * exists that fails if any individual allowlist entry, the unknown-is-fatal default, or the
 * operation gating is removed.
 */
class SnowflakeSourceMetadataQuerierTest {

    companion object {
        private const val DATABASE = "TESTDB"
        private const val SCHEMA = "PUBLIC"
        private const val GOOD_VIEW = "GOOD_VIEW"
        private const val BAD_VIEW = "BAD_VIEW"

        // SQLSTATE 42601 / vendor 2057 = the invalid-view incident ("view declared 92 column(s),
        // but view query produces 93 column(s)") -> tolerable, whole-object.
        private const val SQLSTATE_COMPILE_ERROR = "42601"
        private const val ERRORCODE_VIEW_DECLARED_MISMATCH = 2057
        // SQLSTATE 02000 / vendor 2003 = "object does not exist or not authorized" -> tolerable.
        private const val SQLSTATE_NO_DATA = "02000"
        private const val ERRORCODE_OBJECT_NOT_FOUND = 2003
        // Driver-level network failure: snowflake-jdbc surfaces NETWORK_ERROR/IO_ERROR as
        // SQLSTATE 58030 (class '58', NOT '08') with vendor codes 200015/200016 -> must be fatal.
        private const val SQLSTATE_DRIVER_NETWORK = "58030"
        private const val ERRORCODE_DRIVER_NETWORK = 200015
        // Auth/session token expiry: driver reauthentication codes (e.g. 390114 "Authentication
        // token has expired") default to SQLSTATE XX000 -> must be fatal.
        private const val SQLSTATE_INTERNAL = "XX000"
        private const val ERRORCODE_TOKEN_EXPIRED = 390114
        // "No active warehouse selected": SQLSTATE 57P03 / vendor 401 -> must be fatal.
        private const val SQLSTATE_NO_WAREHOUSE = "57P03"
        private const val ERRORCODE_NO_WAREHOUSE = 401
    }

    /** Holds the mocks so tests can verify interaction counts on the [Statement]. */
    private class Fixture(val querier: SnowflakeSourceMetadataQuerier, val stmt: Statement)

    /** Builds a [SnowflakeSourceMetadataQuerier] whose base delegates to the given [Connection]. */
    private fun querierFor(
        conn: Connection,
        tolerateObjectLevelFailures: Boolean,
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
                checkPrivileges = true,
            )
        // Mock the connection factory (final in the pinned CDK) so the base JdbcMetadataQuerier
        // uses our mocked conn; Mockito 5's inline mock-maker supports final classes.
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

    /** A successful single-column LIMIT 0 probe result set (metadata only). */
    private fun probeResultSet(): ResultSet {
        val meta = mock(ResultSetMetaData::class.java)
        `when`(meta.columnCount).thenReturn(1)
        `when`(meta.getColumnName(1)).thenReturn("ID")
        `when`(meta.getColumnLabel(1)).thenReturn("ID")
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
    ): Fixture {
        val dbmd = mock(DatabaseMetaData::class.java)
        `when`(dbmd.getTables(anyString(), any(), any(), any())).thenAnswer { tablesResultSet() }
        `when`(dbmd.getColumns(any(), any(), any(), any())).thenAnswer { columnsResultSet() }

        // The probe SQL (SELECT ... FROM "PUBLIC"."<view>" LIMIT 0) names the target view, so route
        // by SQL contents: GOOD_VIEW succeeds, BAD_VIEW throws the supplied failure.
        val stmt = mock(Statement::class.java)
        `when`(stmt.executeQuery(contains(BAD_VIEW))).thenThrow(probeFailure)
        `when`(stmt.executeQuery(contains(GOOD_VIEW))).thenAnswer { probeResultSet() }

        val conn = mock(Connection::class.java)
        `when`(conn.metaData).thenReturn(dbmd)
        `when`(conn.createStatement()).thenReturn(stmt)
        return Fixture(querierFor(conn, tolerateObjectLevelFailures), stmt)
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

        // The healthy view still discovers its fields.
        val goodFields = fixture.querier.fields(streamId(GOOD_VIEW))
        assertEquals(1, goodFields.size)
        assertEquals("ID", goodFields.single().id)

        // The broken view yields NO fields instead of failing the whole discover; DiscoverOperation
        // then logs "Ignoring stream ..." and skips it.
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

        // A view whose definition does not compile fails identically for every column, so only the
        // all-columns probe (1 query) may run — no per-column retry storm.
        verify(fixture.stmt, times(1)).executeQuery(contains(BAD_VIEW))
    }

    @Test
    fun `object-not-found vendor code is tolerated even with a null sqlState`() {
        // Pins the errorCode branch of the allowlist independently of SQLSTATE.
        val fixture =
            fixtureWith(
                SQLException("does not exist or not authorized", null, ERRORCODE_OBJECT_NOT_FOUND)
            )

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
    }

    @Test
    fun `no-data sqlState class is tolerated independently of the vendor code`() {
        // Pins the SQLSTATE-class branch of the allowlist: class '02' with an unlisted errorCode.
        val fixture = fixtureWith(SQLException("object not visible", SQLSTATE_NO_DATA, 0))

        assertTrue(fixture.querier.fields(streamId(BAD_VIEW)).isEmpty())
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
        // CHECK relies on a throwing fields() to detect roles that cannot SELECT anything, and
        // READ must fail loudly on a broken selected stream; with tolerance off (the default),
        // even an allowlisted object-level error must propagate.
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
