/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import java.util.UUID;

/**
 * Interface that describe which features are activated in airbyte. Currently the only
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
   * Return true if field selection should be applied for the given workspaceId
   *
   * @param workspaceId that owns the sync
   * @return whether field selection should be applied
   */
  boolean applyFieldSelection(UUID workspaceId);

}
