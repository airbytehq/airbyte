/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async;

import io.airbyte.cdk.integrations.destination.StreamSyncSummary;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;
import java.util.function.BiConsumer;

/**
 * Async version of
 * {@link io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction}.
 * Separately out for easier versioning.
 */
public interface OnCloseFunction extends BiConsumer<Boolean, Map<StreamDescriptor, StreamSyncSummary>> {

}
