/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import io.airbyte.commons.json.JsonSchemas;
import java.io.File;
import java.nio.file.Path;

public enum AirbyteProtocolSchema {

  PROTOCOL("airbyte_protocol.yaml");

  static final Path KNOWN_SCHEMAS_ROOT = JsonSchemas.prepareSchemas("airbyte_protocol", AirbyteProtocolSchema.class);

  private final String schemaFilename;

  AirbyteProtocolSchema(final String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  public File getFile() {
    return KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile();
  }

}
