/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import java.util.HexFormat
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

/**
 * Unit tests for [PostgisGeometry.toEwkt]. Unlike a converter test that feeds fabricated text,
 * these use a real EWKB payload so we assert the actual canonical EWKT produced by postgis-jdbc —
 * the value that lands in the destination on both the snapshot and CDC paths.
 */
class PostgisGeometryTest {

    // EWKB for SRID=4326;POINT(1 2):
    //   01            little-endian
    //   01000020      wkbPoint (0x01) with the EWKB SRID flag (0x20000000)
    //   E6100000      SRID = 4326
    //   000000000000F03F  x = 1.0 (IEEE-754 LE)
    //   0000000000000040  y = 2.0
    private val pointHex = "0101000020E6100000000000000000F03F0000000000000040"
    private val expectedEwkt = "SRID=4326;POINT(1 2)"

    @Test
    fun `hex-EWKB string is normalized to canonical EWKT`() {
        assertEquals(expectedEwkt, PostgisGeometry.toEwkt(pointHex))
    }

    @Test
    fun `raw WKB byte array is normalized to canonical EWKT`() {
        val wkbBytes: ByteArray = HexFormat.of().parseHex(pointHex)
        assertEquals(expectedEwkt, PostgisGeometry.toEwkt(wkbBytes))
    }

    @Test
    fun `EWKT text round-trips unchanged`() {
        assertEquals(expectedEwkt, PostgisGeometry.toEwkt(expectedEwkt))
    }

    @Test
    fun `null input yields null`() {
        assertNull(PostgisGeometry.toEwkt(null))
    }

    @Test
    fun `blank and empty inputs yield null`() {
        assertNull(PostgisGeometry.toEwkt(""))
        assertNull(PostgisGeometry.toEwkt("   "))
        assertNull(PostgisGeometry.toEwkt(ByteArray(0)))
    }
}
