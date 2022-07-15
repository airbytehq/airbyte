/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

public enum ElasticsearchAuthenticationMethod {
  none,
  secret,
  basic
}
