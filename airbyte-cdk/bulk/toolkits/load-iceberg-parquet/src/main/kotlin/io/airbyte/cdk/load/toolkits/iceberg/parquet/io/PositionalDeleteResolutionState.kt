/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

/** Stream-scoped state shared by positional writers created for successive flushes. */
class PositionalDeleteResolutionState {
    internal val warningLogged = AtomicBoolean(false)
    internal val dataFilesOpened = AtomicInteger(0)
    internal val rowsScanned = AtomicLong(0)
}
