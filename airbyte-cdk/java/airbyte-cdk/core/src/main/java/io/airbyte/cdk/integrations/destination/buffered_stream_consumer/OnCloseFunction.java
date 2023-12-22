/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer;

import io.airbyte.cdk.integrations.destination.StreamSyncSummary;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;

/**
 * Interface allowing destination to specify clean up logic that must be executed after all
 * record-related logic has finished.
 * <p>
 * The map of StreamSyncSummaries MUST be non-null, but MAY be empty. Streams not present in the map
 * will be treated as equivalent to {@link StreamSyncSummary#DEFAULT}.
 */
public interface OnCloseFunction extends CheckedBiConsumer<Boolean, Map<StreamDescriptor, StreamSyncSummary>, Exception> {

}
