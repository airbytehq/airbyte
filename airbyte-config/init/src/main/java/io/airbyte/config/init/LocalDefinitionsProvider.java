/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static io.airbyte.config.init.JsonDefinitionsHelper.addMissingCustomField;
import static io.airbyte.config.init.JsonDefinitionsHelper.addMissingPublicField;
import static io.airbyte.config.init.JsonDefinitionsHelper.addMissingTombstoneField;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.io.Resources;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.CombinedConnectorCatalog;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * This provider contains all definitions according to the local yaml files.
 */
final public class LocalDefinitionsProvider implements DefinitionsProvider {

  public static final Class<?> DEFAULT_SEED_DEFINITION_RESOURCE_CLASS = SeedType.class;

  private final static String PROTOCOL_VERSION = "protocol_version";
  private final static String SPEC = "spec";

  private Map<UUID, StandardSourceDefinition> sourceDefinitions;
  private Map<UUID, StandardDestinationDefinition> destinationDefinitions;

  // TODO inject via dependency injection framework
  // QUESTION: Is this nessesary?
  // TODO remove if not
  private final String localCatalogPath;

  public LocalDefinitionsProvider() throws IOException {

    // TODO get the filename from config
    this.localCatalogPath = "seed/oss_catalog.json";
  }

  // TODO (ben): finish this 😅 and write tests
  public CombinedConnectorCatalog getLocalDefinitionCatalog() {
    // TODO add logs
    // TODO add tests
    try {
      final URL url = Resources.getResource(this.localCatalogPath);
      final String jsonString = Resources.toString(url, StandardCharsets.UTF_8);
      final CombinedConnectorCatalog catalog = Jsons.deserialize(jsonString, CombinedConnectorCatalog.class);
      return catalog;

    } catch (final Exception e) {
      throw new RuntimeException("Failed to fetch local catalog definitions", e);
    }
  }

  public Map<UUID, StandardSourceDefinition> getSourceDefinitionsMap() {
    final CombinedConnectorCatalog catalog = getLocalDefinitionCatalog();
    return catalog.getSources().stream().collect(Collectors.toMap(
        StandardSourceDefinition::getSourceDefinitionId,
        source -> source.withProtocolVersion(
            AirbyteProtocolVersion.getWithDefault(source.getSpec() != null ? source.getSpec().getProtocolVersion() : null).serialize())));
  }

  public Map<UUID, StandardDestinationDefinition> getDestinationDefinitionsMap() {
    final CombinedConnectorCatalog catalog = getLocalDefinitionCatalog();
    return catalog.getDestinations().stream().collect(
        Collectors.toMap(
            StandardDestinationDefinition::getDestinationDefinitionId,
            destination -> destination.withProtocolVersion(
                AirbyteProtocolVersion.getWithDefault(
                    destination.getSpec() != null
                        ? destination.getSpec().getProtocolVersion()
                        : null)
                    .serialize())));
  }

  @Override
  public StandardSourceDefinition getSourceDefinition(final UUID definitionId) throws ConfigNotFoundException {
    final StandardSourceDefinition definition = getSourceDefinitionsMap().get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_SOURCE_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardSourceDefinition> getSourceDefinitions() {
    return new ArrayList<>(getSourceDefinitionsMap().values());
  }

  @Override
  public StandardDestinationDefinition getDestinationDefinition(final UUID definitionId) throws ConfigNotFoundException {
    final StandardDestinationDefinition definition = getDestinationDefinitionsMap().get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_DESTINATION_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardDestinationDefinition> getDestinationDefinitions() {
    return new ArrayList<>(getDestinationDefinitionsMap().values());
  }

}
