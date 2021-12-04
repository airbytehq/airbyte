/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

public enum ElasticsearchAuthenticationMethod {
  none,
  secret,
  basic
}
