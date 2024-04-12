/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import java.time.Duration

object DebeziumIteratorConstants {
    const val SYNC_CHECKPOINT_DURATION_PROPERTY: String = "sync_checkpoint_seconds"
    const val SYNC_CHECKPOINT_RECORDS_PROPERTY: String = "sync_checkpoint_records"

    // TODO: Move these variables to a separate class IteratorConstants, as they will be used in
    // state
    // iterators for non debezium cases too.
    @JvmField val SYNC_CHECKPOINT_DURATION: Duration = Duration.ofMinutes(15)
    const val SYNC_CHECKPOINT_RECORDS: Int = 10000
}
