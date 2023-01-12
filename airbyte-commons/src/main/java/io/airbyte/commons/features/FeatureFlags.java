/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

}
