/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

public enum OpenSearchAuthenticationMethod {
  none,
  secret,
  basic
}
