/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.version

/**
 * StarRocks (shared-data) version feature gating — see the connector's `CONTRIBUTING.md`.
 *
 * Detected from `SELECT current_version()` (at `check` and again at write start) and used to (a)
 * reject clusters below the supported floor and (b) opt INTO request-body Stream Load compression
 * when the cluster is new enough (JSON load format only).
 *
 * Floor = shared-data **3.3.x**; the PRIMARY KEY upsert/delete model itself is 3.1.0.
 */
object StarrocksVersionGate {

    data class SemVer(val major: Int, val minor: Int, val patch: Int) : Comparable<SemVer> {
        override fun compareTo(other: SemVer): Int =
            compareValuesBy(this, other, { it.major }, { it.minor }, { it.patch })

        override fun toString(): String = "$major.$minor.$patch"
    }

    // Supported floor: the connector targets shared-data >= 3.3.x. Older clusters are rejected at
    // `check`. (The PK model is 3.1.0, but 3.3 is the deliberate lower bound for the feature set.)
    val MIN_SUPPORTED = SemVer(3, 3, 0)

    // Request-body Stream Load compression (JSON load format only) is supported from this version.
    val MIN_COMPRESSION = SemVer(3, 3, 2)

    data class Capabilities(
        /** Request-body Stream Load compression (gzip/zstd). Honored by StarRocks for JSON only. */
        val compression: Boolean,
    )

    private val VERSION_RE = Regex("""(\d+)\.(\d+)\.(\d+)""")

    fun parse(raw: String): SemVer {
        val m =
            VERSION_RE.find(raw)
                ?: throw IllegalArgumentException("Unrecognized StarRocks version: '$raw'")
        return SemVer(m.groupValues[1].toInt(), m.groupValues[2].toInt(), m.groupValues[3].toInt())
    }

    fun capabilities(raw: String): Capabilities =
        Capabilities(compression = parse(raw) >= MIN_COMPRESSION)

    /** Throws if the cluster is below the supported floor (shared-data >= 3.3.x). */
    fun validate(raw: String) {
        val v = parse(raw)
        if (v < MIN_SUPPORTED) {
            throw IllegalStateException(
                "StarRocks $v is not supported: the connector requires shared-data >= " +
                    "$MIN_SUPPORTED. See the connector docs.",
            )
        }
    }
}
