/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import jakarta.inject.Singleton

/**
 * Whether the Storage Read API may be used by this READ.
 *
 * Determined once per READ by [BigQueryReadApiAvailabilityProbe] before any feed starts: a service
 * account without the BigQuery Read Session User role marks it unavailable, and the whole connector
 * falls back to the query API (the JDBC path, without the driver's `EnableHighThroughputAPI`). It
 * starts out available so that operations which never probe (CHECK, DISCOVER) are unaffected.
 */
@Singleton
class BigQueryReadApiAvailability {
    @Volatile private var unavailableReason: String? = null

    val isAvailable: Boolean
        get() = unavailableReason == null

    /** Why the Read API is not used, or null when it is. */
    val reason: String?
        get() = unavailableReason

    fun markUnavailable(reason: String) {
        unavailableReason = reason
    }

    /** For tests. */
    fun reset() {
        unavailableReason = null
    }
}
