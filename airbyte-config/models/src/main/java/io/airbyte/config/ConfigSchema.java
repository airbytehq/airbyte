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

public enum ConfigSchema implements AirbyteConfig {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.yaml",
      StandardWorkspace.class,
      standardWorkspace -> standardWorkspace.getWorkspaceId().toString(),
      "workspaceId"),

  // source
  STANDARD_SOURCE_DEFINITION("StandardSourceDefinition.yaml",
      StandardSourceDefinition.class,
      standardSourceDefinition -> standardSourceDefinition.getSourceDefinitionId().toString(),
      "sourceDefinitionId"),
  SOURCE_CONNECTION("SourceConnection.yaml",
      SourceConnection.class,
      sourceConnection -> sourceConnection.getSourceId().toString(),
      "sourceId"),

  // destination
  STANDARD_DESTINATION_DEFINITION("StandardDestinationDefinition.yaml",
      StandardDestinationDefinition.class,
      standardDestinationDefinition -> standardDestinationDefinition.getDestinationDefinitionId().toString(),
      "destinationDefinitionId"),
  DESTINATION_CONNECTION("DestinationConnection.yaml",
      DestinationConnection.class,
      destinationConnection -> destinationConnection.getDestinationId().toString(),
      "destinationId"),

  // sync
  STANDARD_SYNC("StandardSync.yaml",
      StandardSync.class,
      standardSync -> standardSync.getConnectionId().toString(),
      "connectionId"),
  STANDARD_SYNC_OPERATION("StandardSyncOperation.yaml",
      StandardSyncOperation.class,
      standardSyncOperation -> standardSyncOperation.getOperationId().toString(),
      "operationId"),

  SOURCE_OAUTH_PARAM("SourceOAuthParameter.yaml", SourceOAuthParameter.class,
      sourceOAuthParameter -> sourceOAuthParameter.getOauthParameterId().toString(),
      "oauthParameterId"),
  DESTINATION_OAUTH_PARAM("DestinationOAuthParameter.yaml", DestinationOAuthParameter.class,
      destinationOAuthParameter -> destinationOAuthParameter.getOauthParameterId().toString(),
      "oauthParameterId"),

  STANDARD_SYNC_SUMMARY("StandardSyncSummary.yaml", StandardSyncSummary.class),

  // worker
  STANDARD_SYNC_INPUT("StandardSyncInput.yaml", StandardSyncInput.class),
  NORMALIZATION_INPUT("NormalizationInput.yaml", NormalizationInput.class),
  OPERATOR_DBT_INPUT("OperatorDbtInput.yaml", OperatorDbtInput.class),
  STANDARD_SYNC_OUTPUT("StandardSyncOutput.yaml", StandardSyncOutput.class),
  REPLICATION_OUTPUT("ReplicationOutput.yaml", ReplicationOutput.class),
  STATE("State.yaml", State.class);

  static final Path KNOWN_SCHEMAS_ROOT = JsonSchemas.prepareSchemas("types", ConfigSchema.class);

  private final String schemaFilename;
  private final Class<?> className;
  private final Function<?, String> extractId;
  private final String idFieldName;

  <T> ConfigSchema(final String schemaFilename,
                   Class<T> className,
                   Function<T, String> extractId,
                   String idFieldName) {
    this.schemaFilename = schemaFilename;
    this.className = className;
    this.extractId = extractId;
    this.idFieldName = idFieldName;
  }

  <T> ConfigSchema(final String schemaFilename,
                   Class<T> className) {
    this.schemaFilename = schemaFilename;
    this.className = className;
    this.extractId = object -> {
      throw new RuntimeException(className.getSimpleName() + " doesn't have an id");
    };
    this.idFieldName = null;
  }

  @Override
  public File getConfigSchemaFile() {
    return KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile();
  }

  public <T> Class<T> getClassName() {
    return (Class<T>) className;
  }

  @Override
  public <T> String getId(T object) {
    if (getClassName().isInstance(object)) {
      return ((Function<T, String>) extractId).apply(object);
    }
    throw new RuntimeException("Object: " + object + " is not instance of class " + getClassName().getName());
  }

  @Override
  public String getIdFieldName() {
    return idFieldName;
  }

}
