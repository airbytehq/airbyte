/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.List;
import java.util.Map;

public interface DestinationHandler<DestinationState> {

  void execute(final Sql sql) throws Exception;

  /**
   * Fetch the current state of the destination for the given streams. This method MUST create the
   * airbyte_internal.state table if it does not exist. This method MAY assume the airbyte_internal
   * schema already exists. (substitute the appropriate raw table schema if the user is overriding
   * it).
   */
  List<DestinationInitialStatus<DestinationState>> gatherInitialState(List<StreamConfig> streamConfigs) throws Exception;

  void commitDestinationStates(final Map<StreamId, DestinationState> destinationStates) throws Exception;

}
