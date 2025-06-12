/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.operation;

import io.airbyte.integrations.base.destination.operation.StreamOperation;
import io.airbyte.integrations.base.destination.operation.StreamOperationFactory;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import org.jetbrains.annotations.NotNull;

public class SingleStoreStreamOperationFactory implements StreamOperationFactory<MinimumDestinationState.Impl> {

  private final SingleStoreStorageOperations storageOperations;

  public SingleStoreStreamOperationFactory(SingleStoreStorageOperations storageOperations) {
    this.storageOperations = storageOperations;
  }

  @NotNull
  @Override
  public StreamOperation<MinimumDestinationState.Impl> createInstance(@NotNull DestinationInitialStatus<MinimumDestinationState.Impl> destinationInitialStatus,
                                                                      boolean disableTypeDedupe) {
    return new SingleStoreStreamOperation(storageOperations, destinationInitialStatus, disableTypeDedupe);
  }

}
