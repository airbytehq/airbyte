/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.handlers.SourceDefinitionsHandler;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class SourceHelpers {

  public static SourceConnection generateSource(final UUID sourceDefinitionId) throws IOException {
    return generateSource(sourceDefinitionId, "my default source name", false);
  }

  public static SourceConnection generateSource(final UUID sourceDefinitionId, final String name) throws IOException {
    return generateSource(sourceDefinitionId, name, false);
  }

  public static SourceConnection generateSource(final UUID sourceDefinitionId, final boolean tombstone) throws IOException {
    return generateSource(sourceDefinitionId, "my default source name", tombstone);
  }

  public static SourceConnection generateSource(final UUID sourceDefinitionId, final String name, final boolean tombstone) throws IOException {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();

    final JsonNode implementationJson = getTestImplementationJson();

    return new SourceConnection()
        .withName(name)
        .withWorkspaceId(workspaceId)
        .withSourceDefinitionId(sourceDefinitionId)
        .withSourceId(sourceId)
        .withConfiguration(implementationJson)
        .withTombstone(tombstone);
  }

  public static JsonNode getTestImplementationJson() throws IOException {
    final Path path = Paths.get(SourceHelpers.class.getClassLoader().getResource("json/TestImplementation.json").getPath());
    return Jsons.deserialize(Files.readString(path));
  }

  public static SourceRead getSourceRead(final SourceConnection source, final StandardSourceDefinition standardSourceDefinition) {

    return new SourceRead()
        .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .workspaceId(source.getWorkspaceId())
        .sourceDefinitionId(source.getSourceDefinitionId())
        .sourceId(source.getSourceId())
        .connectionConfiguration(source.getConfiguration())
        .name(source.getName())
        .sourceName(standardSourceDefinition.getName())
        .icon(SourceDefinitionsHandler.loadIcon(standardSourceDefinition.getIcon()));
  }

}
