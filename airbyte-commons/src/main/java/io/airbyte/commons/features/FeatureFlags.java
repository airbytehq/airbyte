/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

/**
 * Interface that describe which features are activated in airbyte. Currently the only
 * implementation relies on env. Ideally it should be on some DB.
 */
public interface FeatureFlags {

  boolean autoDisablesFailingConnections();

  boolean exposeSecretsInExport();

  boolean forceSecretMigration();

  boolean useStreamCapableState();

}
