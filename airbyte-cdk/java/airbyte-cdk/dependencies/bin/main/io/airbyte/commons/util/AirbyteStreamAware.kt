/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import java.util.*

/**
 * Interface that indicates that an object exposes information used to identify an Airbyte stream.
 */
interface AirbyteStreamAware {
    /**
     * Returns the [AirbyteStreamNameNamespacePair] identifying the Airbyte stream associated with
     * the object.
     */
    val airbyteStream: Optional<AirbyteStreamNameNamespacePair>
        get() = Optional.empty()
}
