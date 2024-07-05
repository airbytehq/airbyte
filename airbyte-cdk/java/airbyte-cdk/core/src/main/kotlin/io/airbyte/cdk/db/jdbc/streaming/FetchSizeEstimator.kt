/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import java.util.*
import java.util.function.Consumer

interface FetchSizeEstimator : Consumer<Any> {
    /** @return the estimated fetch size when the estimation is ready */
    val fetchSize: Optional<Int>
}
