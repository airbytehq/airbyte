/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

public enum SeedConnectorType {

  SOURCE(
      "source_definitions.yaml",
      "source_specs.yaml"),
  DESTINATION(
      "destination_definitions.yaml",
      "destination_specs.yaml");

  private final String definitionFileName;
  private final String specFileName;

  SeedConnectorType(final String definitionFileName,
                    final String specFileName) {
    this.definitionFileName = definitionFileName;
    this.specFileName = specFileName;
  }

  public String getDefinitionFileName() {
    return definitionFileName;
  }

  public String getSpecFileName() {
    return specFileName;
  }

}
