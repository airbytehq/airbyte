/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import io.airbyte.protocol.models.v0.DestinationSyncMode;

public record RedpandaWriteConfig(

                                  String topicName,

                                  DestinationSyncMode destinationSyncMode

) {}
