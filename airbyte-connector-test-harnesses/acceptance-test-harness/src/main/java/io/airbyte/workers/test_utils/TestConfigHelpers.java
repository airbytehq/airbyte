/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.test_utils;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.configoss.DestinationConnection;
import io.airbyte.configoss.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.configoss.OperatorDbt;
import io.airbyte.configoss.OperatorNormalization;
import io.airbyte.configoss.OperatorNormalization.Option;
import io.airbyte.configoss.SourceConnection;
import io.airbyte.configoss.StandardSyncInput;
import io.airbyte.configoss.StandardSyncOperation;
import io.airbyte.configoss.StandardSyncOperation.OperatorType;
import io.airbyte.configoss.State;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class TestConfigHelpers {

  private static final String CONNECTION_NAME = "favorite_color_pipe";
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final long LAST_SYNC_TIME = 1598565106;

  public static ImmutablePair<Void, StandardSyncInput> createSyncConfig() {
    return createSyncConfig(false);
  }

  public static ImmutablePair<Void, StandardSyncInput> createSyncConfig(final Boolean multipleNamespaces) {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final UUID destinationDefinitionId = UUID.randomUUID();
    final UUID destinationId = UUID.randomUUID();
    final UUID normalizationOperationId = UUID.randomUUID();
    final UUID dbtOperationId = UUID.randomUUID();

    final JsonNode sourceConnection =
        Jsons.jsonNode(
            Map.of(
                "apiKey", "123",
                "region", "us-east"));

    final JsonNode destinationConnection =
        Jsons.jsonNode(
            Map.of(
                "username", "airbyte",
                "token", "anau81b"));

    final SourceConnection sourceConnectionConfig = new SourceConnection()
        .withConfiguration(sourceConnection)
        .withWorkspaceId(workspaceId)
        .withSourceDefinitionId(sourceDefinitionId)
        .withSourceId(sourceId)
        .withTombstone(false);

    final DestinationConnection destinationConnectionConfig = new DestinationConnection()
        .withConfiguration(destinationConnection)
        .withWorkspaceId(workspaceId)
        .withDestinationDefinitionId(destinationDefinitionId)
        .withDestinationId(destinationId)
        .withTombstone(false);

    final StandardSyncOperation normalizationOperation = new StandardSyncOperation()
        .withOperationId(normalizationOperationId)
        .withName("Normalization")
        .withOperatorType(OperatorType.NORMALIZATION)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
        .withTombstone(false);

    final StandardSyncOperation customDbtOperation = new StandardSyncOperation()
        .withOperationId(dbtOperationId)
        .withName("Custom Transformation")
        .withOperatorType(OperatorType.DBT)
        .withOperatorDbt(new OperatorDbt()
            .withDockerImage("docker")
            .withDbtArguments("--help")
            .withGitRepoUrl("git url")
            .withGitRepoBranch("git url"))
        .withTombstone(false);

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog();
    if (multipleNamespaces) {
      final ConfiguredAirbyteStream streamOne = new ConfiguredAirbyteStream()
          .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME, "namespace", Field.of(FIELD_NAME, JsonSchemaType.STRING)));
      final ConfiguredAirbyteStream streamTwo = new ConfiguredAirbyteStream()
          .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME, "namespace2", Field.of(FIELD_NAME, JsonSchemaType.STRING)));

      final List<ConfiguredAirbyteStream> streams = List.of(streamOne, streamTwo);
      catalog.withStreams(streams);

    } else {
      final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream()
          .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME, Field.of(FIELD_NAME, JsonSchemaType.STRING)));
      catalog.withStreams(Collections.singletonList(stream));
    }

    final String stateValue = Jsons.serialize(Map.of("lastSync", String.valueOf(LAST_SYNC_TIME)));

    final State state = new State().withState(Jsons.jsonNode(stateValue));

    final StandardSyncInput syncInput = new StandardSyncInput()
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withPrefix(CONNECTION_NAME)
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withDestinationConfiguration(destinationConnectionConfig.getConfiguration())
        .withCatalog(catalog)
        .withSourceConfiguration(sourceConnectionConfig.getConfiguration())
        .withState(state)
        .withOperationSequence(List.of(normalizationOperation, customDbtOperation))
        .withWorkspaceId(workspaceId);

    return new ImmutablePair<>(null, syncInput);
  }

}
