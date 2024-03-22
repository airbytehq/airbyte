/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

public enum SeedType {

  STANDARD_SOURCE_DEFINITION("/seed/source_definitions.yaml", "sourceDefinitionId"),
  STANDARD_DESTINATION_DEFINITION("/seed/destination_definitions.yaml", "destinationDefinitionId"),
  SOURCE_SPEC("/seed/source_specs.yaml", "dockerImage"),
  DESTINATION_SPEC("/seed/destination_specs.yaml", "dockerImage"),
  SOURCE_OAUTH_PARAM("/seed/source_oauth.yaml", "oauthParameterId"),
  DESTINATION_OAUTH_PARAM("/seed/destination_oauth.yaml", "oauthParameterId");

  final String resourcePath;
  // ID field name
  final String idName;

  SeedType(final String resourcePath, final String idName) {
    this.resourcePath = resourcePath;
    this.idName = idName;
  }

  public String getResourcePath() {
    return resourcePath;
  }

  public String getIdName() {
    return idName;
  }

}
