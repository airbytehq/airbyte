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

package io.airbyte.config;

import io.airbyte.commons.json.JsonSchemas;
import java.io.File;
import java.nio.file.Path;

public enum ConfigSchema {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.yaml"),

  // source
  STANDARD_SOURCE_DEFINITION("StandardSourceDefinition.yaml"),
  SOURCE_CONNECTION("SourceConnection.yaml"),

  // destination
  STANDARD_DESTINATION_DEFINITION("StandardDestinationDefinition.yaml"),
  DESTINATION_CONNECTION("DestinationConnection.yaml"),

  // sync
  STANDARD_SYNC("StandardSync.yaml"),
  STANDARD_SYNC_OPERATION("StandardSyncOperation.yaml"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.yaml"),

  // worker
  STANDARD_SYNC_INPUT("StandardSyncInput.yaml"),
  NORMALIZATION_INPUT("NormalizationInput.yaml"),
  OPERATOR_DBT_INPUT("OperatorDbtInput.yaml"),

  STANDARD_SYNC_OUTPUT("StandardSyncOutput.yaml"),
  REPLICATION_OUTPUT("ReplicationOutput.yaml"),

  STATE("State.yaml");

  static final Path KNOWN_SCHEMAS_ROOT = JsonSchemas.prepareSchemas("types", ConfigSchema.class);

  private final String schemaFilename;

  ConfigSchema(final String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  public File getFile() {
    return KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile();
  }

}
