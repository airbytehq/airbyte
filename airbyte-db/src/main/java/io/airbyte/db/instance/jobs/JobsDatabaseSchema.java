/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
    File schemaFile = SCHEMAS_ROOT.resolve(schemaFilename).toFile();
    return JsonSchemaValidator.getSchema(schemaFile);
  }

  /**
   * @return table names in lower case
   */
  public static Set<String> getTableNames() {
    return Stream.of(JobsDatabaseSchema.values()).map(JobsDatabaseSchema::getTableName).collect(Collectors.toSet());
  }

}
