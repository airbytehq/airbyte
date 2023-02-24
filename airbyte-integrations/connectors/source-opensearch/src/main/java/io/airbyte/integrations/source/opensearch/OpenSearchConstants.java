/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch;

public class OpenSearchConstants {

  private OpenSearchConstants() {}

  public static final String REGEX_FOR_USER_INDICES_ONLY = "(^\\.)|(metrics-endpoint.metadata_current_default)";
  public static final String ALL_INDICES_QUERY = "*";

}
