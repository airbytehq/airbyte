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
import java.util.function.Function;

public enum ConfigSchema {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.yaml", StandardWorkspace.class, standardWorkspace -> {
    return standardWorkspace.getWorkspaceId().toString();
  }),

  // source
  STANDARD_SOURCE_DEFINITION("StandardSourceDefinition.yaml", StandardSourceDefinition.class,
      standardSourceDefinition -> {
        return standardSourceDefinition.getSourceDefinitionId().toString();
      }),
  SOURCE_CONNECTION("SourceConnection.yaml", SourceConnection.class,
      sourceConnection -> {
        return sourceConnection.getSourceId().toString();
      }),

  // destination
  STANDARD_DESTINATION_DEFINITION("StandardDestinationDefinition.yaml",
      StandardDestinationDefinition.class, standardDestinationDefinition -> {
        return standardDestinationDefinition.getDestinationDefinitionId().toString();
      }),
  DESTINATION_CONNECTION("DestinationConnection.yaml", DestinationConnection.class,
      destinationConnection -> {
        return destinationConnection.getDestinationId().toString();
      }),

  // sync
  STANDARD_SYNC("StandardSync.yaml", StandardSync.class, standardSync -> {
    return standardSync.getConnectionId().toString();
  }),
  STANDARD_SYNC_OPERATION("StandardSyncOperation.yaml", StandardSyncOperation.class,
      standardSyncOperation -> {
        return standardSyncOperation.getOperationId().toString();
      }),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.yaml", StandardSyncSummary.class,
      standardSyncSummary -> {
        throw new RuntimeException("No Id for StandardSyncSummary exists");
      }),

  // worker
  STANDARD_SYNC_INPUT("StandardSyncInput.yaml", StandardSyncInput.class,
      standardSyncInput -> {
        throw new RuntimeException("No Id for StandardSyncInput exists");
      }),
  NORMALIZATION_INPUT("NormalizationInput.yaml", NormalizationInput.class,
      normalizationInput -> {
        throw new RuntimeException("No Id for NormalizationInput exists");
      }),
  OPERATOR_DBT_INPUT("OperatorDbtInput.yaml", OperatorDbtInput.class,
      operatorDbtInput -> {
        throw new RuntimeException("No Id for OperatorDbtInput exists");
      }),

  STANDARD_SYNC_OUTPUT("StandardSyncOutput.yaml", StandardSyncOutput.class,
      standardWorkspace -> {
        throw new RuntimeException("No Id for StandardSyncOutput exists");
      }),
  REPLICATION_OUTPUT("ReplicationOutput.yaml", ReplicationOutput.class,
      standardWorkspace -> {
        throw new RuntimeException("No Id for ReplicationOutput exists");
      }),

  STATE("State.yaml", State.class, standardWorkspace -> {
    throw new RuntimeException("No Id for State exists");
  });

  static final Path KNOWN_SCHEMAS_ROOT = JsonSchemas.prepareSchemas("types", ConfigSchema.class);

  private final String schemaFilename;
  private final Class<?> className;
  private final Function<?, String> extractId;

  <T> ConfigSchema(final String schemaFilename,
                   Class<T> className,
                   Function<T, String> extractId) {
    this.schemaFilename = schemaFilename;
    this.className = className;
    this.extractId = extractId;
  }

  public File getFile() {
    return KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile();
  }

  public <T> Class<T> getClassName() {
    return (Class<T>) className;
  }

  public <T> String getId(T object) {
    if (getClassName().isInstance(object)) {
      return ((Function<T, String>) extractId).apply(object);
    }
    throw new RuntimeException(
        "Object: " + object + " is not instance of class " + getClassName().getName());
  }

}
