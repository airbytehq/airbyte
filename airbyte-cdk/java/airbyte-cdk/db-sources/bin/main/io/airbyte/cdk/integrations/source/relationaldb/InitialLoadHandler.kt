/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb

import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.time.Duration
import java.time.Instant
import java.util.Optional

interface InitialLoadHandler<T> {
    fun getIteratorForStream(
        airbyteStream: ConfiguredAirbyteStream,
        table: TableInfo<CommonField<T>>,
        emittedAt: Instant,
        cdcInitialLoadTimeout: Optional<Duration>,
    ): AutoCloseableIterator<AirbyteMessage>
}
