/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch;

public class ElasticsearchConstants {

  private ElasticsearchConstants() {}

  public static final String REGEX_FOR_USER_INDICES_ONLY = "(^\\.)|(metrics-endpoint.metadata_current_default)";
  public static final String ALL_INDICES_QUERY = "*";

}
