/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public record DestinationInitialStateImpl(StreamConfig streamConfig,
                                          boolean isFinalTablePresent,
                                          InitialRawTableState initialRawTableState,
                                          boolean isSchemaMismatch,
                                          boolean isFinalTableEmpty)
    implements DestinationInitialState {

}
