/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql

// Constants defined in
// airbyte-integrations/connectors/source-mssql/src/main/resources/spec.json.
object MsSqlSpecConstants {
    const val INVALID_CDC_CURSOR_POSITION_PROPERTY: String = "invalid_cdc_cursor_position_behavior"
    const val FAIL_SYNC_OPTION: String = "Fail sync"
    const val RESYNC_DATA_OPTION: String = "Re-sync data"
}
