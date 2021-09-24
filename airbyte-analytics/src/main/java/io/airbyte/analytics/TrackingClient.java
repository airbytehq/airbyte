/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import java.util.Map;
import java.util.UUID;

public interface TrackingClient {

  void identify(UUID workspaceId);

  void alias(UUID workspaceId, String previousCustomerId);

  void track(UUID workspaceId, String action);

  void track(UUID workspaceId, String action, Map<String, Object> metadata);

}
