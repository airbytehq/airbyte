/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch;

public enum ElasticsearchAuthenticationMethod {
  none,
  secret,
  basic
}
