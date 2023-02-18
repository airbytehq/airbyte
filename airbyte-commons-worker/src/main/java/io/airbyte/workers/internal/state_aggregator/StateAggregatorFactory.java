/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.state_aggregator;

import io.airbyte.commons.features.FeatureFlags;

public class StateAggregatorFactory {

  final FeatureFlags featureFlags;

  public StateAggregatorFactory(final FeatureFlags featureFlags) {
    this.featureFlags = featureFlags;
  }

  public StateAggregator create() {
    return new DefaultStateAggregator(featureFlags.useStreamCapableState());
  }

}
