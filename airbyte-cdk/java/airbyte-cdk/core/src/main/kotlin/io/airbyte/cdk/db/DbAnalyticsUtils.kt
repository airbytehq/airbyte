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

    fun cdcCursorInvalidMessage(): AirbyteAnalyticsTraceMessage {
        return AirbyteAnalyticsTraceMessage().withType(CDC_CURSOR_INVALID_KEY).withValue("1")
    }
}
