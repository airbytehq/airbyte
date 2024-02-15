/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.state;

import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;

public record PartialStateWithDestinationStats(PartialAirbyteMessage stateMessage, AirbyteStateStats stats, long stateArrivalNumber) {}
