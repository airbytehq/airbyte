/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

/**
 * Interface that describe which features are activated in airbyte. Currently, the only
 * implementation relies on env. Ideally it should be on some DB.
 */
public interface FeatureFlags {

  boolean autoDisablesFailingConnections();

  boolean forceSecretMigration();

  boolean useStreamCapableState();

  boolean autoDetectSchema();

  boolean logConnectorMessages();

  boolean needStateValidation();

  /**
   * Return true if field selection should be applied. See also fieldSelectionWorkspaces.
   *
   * @return whether field selection should be applied
   */
  boolean applyFieldSelection();

  /**
   * Get the workspaces allow-listed for field selection. This should take precedence over
   * applyFieldSelection.
   *
   * @return a comma-separated list of workspace ids where field selection should be enabled.
   */
  String fieldSelectionWorkspaces();

  /**
   * Get the workspaces allow-listed for strict incremental comparison in normalization. This takes
   * precedence over the normalization version in destination_definitions.yaml.
   *
   * @return a comma-separated list of workspace ids where strict incremental comparison should be
   *         enabled in normalization.
   */
  String strictComparisonNormalizationWorkspaces();

  /**
   * @return The Docker image tag representing the normalization version with strict-comparison
   */
  String strictComparisonNormalizationTag();

}
