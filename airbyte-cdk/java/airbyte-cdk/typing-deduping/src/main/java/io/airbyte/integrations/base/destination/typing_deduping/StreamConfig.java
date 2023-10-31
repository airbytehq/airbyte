/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;

public record StreamConfig(StreamId id,
                           SyncMode syncMode,
                           DestinationSyncMode destinationSyncMode,
                           List<ColumnId> primaryKey,
                           Optional<ColumnId> cursor,
                           LinkedHashMap<ColumnId, AirbyteType> columns) {

}
