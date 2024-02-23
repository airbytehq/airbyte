/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

/**
 * Interface representing the initial state of a destination table.
 *
 */
public interface DestinationInitialState {

  StreamConfig streamConfig();

  boolean isFinalTablePresent();

  InitialRawTableState initialRawTableState();

  boolean isSchemaMismatch();

  boolean isFinalTableEmpty();

}
