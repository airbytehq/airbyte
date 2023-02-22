/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

public enum OpenSearchAuthenticationMethod {
  none,
  secret,
  basic
}
