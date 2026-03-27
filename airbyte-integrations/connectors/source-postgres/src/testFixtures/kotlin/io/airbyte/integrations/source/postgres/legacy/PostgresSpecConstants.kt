/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

// Constants defined in PostgresSourceConfigurationSpecification
object PostgresSpecConstants {
    const val INVALID_CDC_CURSOR_POSITION_PROPERTY: String = "invalid_cdc_cursor_position_behavior"
    const val FAIL_SYNC_OPTION: String = "Fail sync"
    const val RESYNC_DATA_OPTION: String = "Re-sync data"
}
