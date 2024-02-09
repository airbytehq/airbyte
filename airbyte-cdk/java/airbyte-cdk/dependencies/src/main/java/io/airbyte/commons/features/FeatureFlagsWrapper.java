/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

public class FeatureFlagsWrapper implements FeatureFlags {

  /**
   * Overrides the {@link FeatureFlags#deploymentMode} method in the feature flags.
   */
  static public FeatureFlags overridingDeploymentMode(
                                                      final FeatureFlags wrapped,
                                                      final String deploymentMode) {
    return new FeatureFlagsWrapper(wrapped) {

      @Override
      public String deploymentMode() {
        return deploymentMode;
      }

    };
  }

  private final FeatureFlags wrapped;

  public FeatureFlagsWrapper(FeatureFlags wrapped) {
    this.wrapped = wrapped;
  }

  @Override
  public boolean autoDetectSchema() {
    return wrapped.autoDetectSchema();
  }

  @Override
  public boolean logConnectorMessages() {
    return wrapped.logConnectorMessages();
  }

  @Override
  public boolean concurrentSourceStreamRead() {
    return wrapped.concurrentSourceStreamRead();
  }

  @Override
  public boolean applyFieldSelection() {
    return wrapped.applyFieldSelection();
  }

  @Override
  public String fieldSelectionWorkspaces() {
    return wrapped.fieldSelectionWorkspaces();
  }

  @Override
  public String strictComparisonNormalizationWorkspaces() {
    return wrapped.strictComparisonNormalizationWorkspaces();
  }

  @Override
  public String strictComparisonNormalizationTag() {
    return wrapped.strictComparisonNormalizationTag();
  }

  @Override
  public String deploymentMode() {
    return wrapped.deploymentMode();
  }

}
