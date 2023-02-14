/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

public enum OpensearchAuthenticationMethod {
  none,
  secret,
  basic
}
