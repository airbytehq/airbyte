/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.function.BiConsumer

/**
 * Async version of
 * [io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction].
 * Separately out for easier versioning.
 */
interface OnCloseFunction :
    BiConsumer<Boolean?, Map<StreamDescriptor?, StreamSyncSummary?>?>
