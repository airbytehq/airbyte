/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.db.instance.TableSchema;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.File;
import java.nio.file.Path;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public enum ConfigsDatabaseSchema2 implements TableSchema {

  // TODO : NOT correct
  WORKSPACE("StandardWorkspace.yaml"),
  ACTOR_DEFINITION(""),
  ACTOR(""),
  ACTOR_OAUTH_PARAMETER(""),
  OPERATION("StandardSyncOperation.yaml"),
  CONNECTION("StandardSync.yaml"),
  CONNECTION_OPERATION(""),
  STATE("StandardSyncState.yaml");

  static final Path SCHEMAS_ROOT = JsonSchemas.prepareSchemas("configs_database", ConfigsDatabaseSchema2.class);

  private final String schemaFilename;

  ConfigsDatabaseSchema2(final String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  @Override
  public String getTableName() {

    return name().toLowerCase();
  }

  @Override
  public JsonNode getTableDefinition() {
    final File schemaFile = SCHEMAS_ROOT.resolve(schemaFilename).toFile();
    return JsonSchemaValidator.getSchema(schemaFile);
  }

  /**
   * @return table names in lower case
   */
  public static Set<String> getTableNames() {
    return Stream.of(ConfigsDatabaseSchema2.values()).map(ConfigsDatabaseSchema2::getTableName).collect(Collectors.toSet());
  }

}
