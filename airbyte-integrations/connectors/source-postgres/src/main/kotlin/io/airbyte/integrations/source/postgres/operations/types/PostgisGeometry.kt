/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import java.util.HexFormat
import org.postgis.PGgeometry

/**
 * Normalizes the various runtime representations of a PostGIS `geometry`/`geography` value into
 * canonical EWKT (e.g. `"SRID=4326;POINT(11.5 48.1)"`), matching PostgreSQL's `ST_AsEWKT`.
 *
 * The same value reaches us in different shapes depending on the sync path:
 * - **Snapshot** (`ResultSet.getString`): a hex-encoded EWKB string such as `0101000020E6100000…`.
 * - **CDC** (Debezium custom converter): either the raw WKB `ByteArray`, the hex-EWKB `String`, or a
 *   driver `PGgeometry` once `postgis-jdbc` is on the classpath. The precise form is connector- and
 *   Debezium-version dependent, so we accept all of them rather than assume one.
 *
 * Producing the identical EWKT on both paths honors the connector's "CDC and non-CDC output format
 * should be the same" principle. Returns `null` for `null`/blank input.
 */
object PostgisGeometry {

    fun toEwkt(value: Any?): String? =
        when (value) {
            null -> null
            is PGgeometry -> value.toString()
            is ByteArray -> if (value.isEmpty()) null else parse(HexFormat.of().formatHex(value))
            is CharSequence -> value.toString().trim().ifBlank { null }?.let(::parse)
            else -> value.toString().trim().ifBlank { null }?.let(::parse)
        }

    // PGgeometry's String constructor parses both hex-EWKB and EWKT text; toString() emits canonical
    // EWKT including the "SRID=<n>;" prefix when an SRID is present.
    private fun parse(hexOrEwkt: String): String = PGgeometry(hexOrEwkt).toString()
}
