/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import io.airbyte.protocol.models.DestinationSyncMode;

public record RedpandaWriteConfig(

                                  String topicName,

                                  DestinationSyncMode destinationSyncMode

) {}
