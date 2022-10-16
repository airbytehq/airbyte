/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.db.instance.TableSchema;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.File;
import java.nio.file.Path;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Whenever a new table is created in the Job Airbyte Database, we should also add a corresponding
 * yaml file to validate the content of the table when it is exported/imported in files.
 *
 * This enum maps the table names to the yaml file where the Json Schema is stored.
 */
public enum JobsDatabaseSchema implements TableSchema {

  ATTEMPTS("Attempts.yaml"),
  JOBS("Jobs.yaml"),
  AIRBYTE_METADATA("AirbyteMetadata.yaml");

  static final Path SCHEMAS_ROOT = JsonSchemas.prepareSchemas("jobs_database", JobsDatabaseSchema.class);

  private final String schemaFilename;

  JobsDatabaseSchema(final String schemaFilename) {
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
    return Stream.of(JobsDatabaseSchema.values()).map(JobsDatabaseSchema::getTableName).collect(Collectors.toSet());
  }

}
