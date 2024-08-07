/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import io.airbyte.protocol.models.v0.AirbyteAnalyticsTraceMessage

/**
 * Utility class to define constants associated with database source connector analytics events.
 * Make sure to add the analytics event to
 * https://www.notion.so/Connector-Analytics-Events-892a79a49852465f8d59a18bd84c36de
 */
object DbAnalyticsUtils {
    const val CDC_CURSOR_INVALID_KEY: String = "db-sources-cdc-cursor-invalid"
    const val DATA_TYPES_SERIALIZATION_ERROR_KEY = "db-sources-data-serialization-error"
    const val CDC_SNAPSHOT_FORCE_SHUTDOWN_KEY = "db-sources-snapshot-force-shutdown"
    const val DEBEZIUM_CLOSE_REASON_KEY = "db-sources-debezium-close-reason"
    const val WASS_OCCURRENCE_KEY = "db-sources-wass-occurrence"
    const val CDC_RESYNC_KEY = "db-sources-cdc-resync"
    const val DEBEZIUM_SHUTDOWN_ERROR = "debezium-shutdown-error"

    @JvmStatic
    fun cdcCursorInvalidMessage(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage().withType(CDC_CURSOR_INVALID_KEY).withValue("1")
    }

    @JvmStatic
    fun dataTypesSerializationErrorMessage(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage()
            .withType(DATA_TYPES_SERIALIZATION_ERROR_KEY)
            .withValue("1")
    }

    @JvmStatic
    fun cdcSnapshotForceShutdownMessage(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage()
            .withType(CDC_SNAPSHOT_FORCE_SHUTDOWN_KEY)
            .withValue("1")
    }

    @JvmStatic
    fun debeziumCloseReasonMessage(reason: String): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage().withType(DEBEZIUM_CLOSE_REASON_KEY).withValue(reason)
    }

    @JvmStatic
    fun wassOccurrenceMessage(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage().withType(WASS_OCCURRENCE_KEY).withValue("1")
    }

    @JvmStatic
    fun cdcResyncMessage(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage().withType(CDC_RESYNC_KEY).withValue("1")
    }

    @JvmStatic
    fun debeziumShutdownError(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage().withType(DEBEZIUM_SHUTDOWN_ERROR).withValue("1")
    }
}
