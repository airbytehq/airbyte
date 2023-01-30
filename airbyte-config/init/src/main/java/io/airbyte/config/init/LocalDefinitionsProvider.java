/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static io.airbyte.config.init.JsonDefinitionsHelper.addMissingCustomField;
import static io.airbyte.config.init.JsonDefinitionsHelper.addMissingPublicField;
import static io.airbyte.config.init.JsonDefinitionsHelper.addMissingTombstoneField;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.io.Resources;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
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
  private final Class<?> seedResourceClass;

  public LocalDefinitionsProvider(final Class<?> seedResourceClass) throws IOException {
    this.seedResourceClass = seedResourceClass;

    // TODO remove this call once dependency injection framework manages object creation
    initialize();
  }

  // TODO will be called automatically by the dependency injection framework on object creation
  public void initialize() throws IOException {
    this.sourceDefinitions =
        parseDefinitions(this.seedResourceClass, SeedType.STANDARD_SOURCE_DEFINITION.getResourcePath(), SeedType.SOURCE_SPEC.getResourcePath(),
            SeedType.STANDARD_SOURCE_DEFINITION.getIdName(), SeedType.SOURCE_SPEC.getIdName(), StandardSourceDefinition.class);
    this.destinationDefinitions = parseDefinitions(this.seedResourceClass, SeedType.STANDARD_DESTINATION_DEFINITION.getResourcePath(),
        SeedType.DESTINATION_SPEC.getResourcePath(), SeedType.STANDARD_DESTINATION_DEFINITION.getIdName(), SeedType.DESTINATION_SPEC.getIdName(),
        StandardDestinationDefinition.class);
  }

  @Override
  public StandardSourceDefinition getSourceDefinition(final UUID definitionId) throws ConfigNotFoundException {
    final StandardSourceDefinition definition = this.sourceDefinitions.get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_SOURCE_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardSourceDefinition> getSourceDefinitions() {
    return new ArrayList<>(this.sourceDefinitions.values());
  }

  @Override
  public StandardDestinationDefinition getDestinationDefinition(final UUID definitionId) throws ConfigNotFoundException {
    final StandardDestinationDefinition definition = this.destinationDefinitions.get(definitionId);
    if (definition == null) {
      throw new ConfigNotFoundException(SeedType.STANDARD_DESTINATION_DEFINITION.name(), definitionId.toString());
    }
    return definition;
  }

  @Override
  public List<StandardDestinationDefinition> getDestinationDefinitions() {
    return new ArrayList<>(this.destinationDefinitions.values());
  }

  @SuppressWarnings("UnstableApiUsage")
  private static <T> Map<UUID, T> parseDefinitions(final Class<?> seedDefinitionsResourceClass,
                                                   final String definitionsYamlPath,
                                                   final String specYamlPath,
                                                   final String definitionIdField,
                                                   final String specIdField,
                                                   final Class<T> definitionModel)
      throws IOException {
    final Map<String, JsonNode> rawDefinitions = getJsonElements(seedDefinitionsResourceClass, definitionsYamlPath, definitionIdField);
    final Map<String, JsonNode> rawSpecs = getJsonElements(seedDefinitionsResourceClass, specYamlPath, specIdField);

    return rawDefinitions.entrySet().stream()
        .collect(Collectors.toMap(e -> UUID.fromString(e.getKey()), e -> {
          final JsonNode withMissingFields = addMissingFields(e.getValue());
          final ObjectNode withSpec = (ObjectNode) mergeSpecIntoDefinition(withMissingFields, rawSpecs);
          final String protocolVersion =
              withSpec.has(SPEC) && withSpec.get(SPEC).has(PROTOCOL_VERSION) ? withSpec.get(SPEC).get(PROTOCOL_VERSION).asText() : null;
          withSpec.put("protocolVersion", AirbyteProtocolVersion.getWithDefault(protocolVersion).serialize());
          return Jsons.object(withSpec, definitionModel);
        }));

  }

  private static Map<String, JsonNode> getJsonElements(final Class<?> seedDefinitionsResourceClass, final String resourcePath, final String idName)
      throws IOException {
    final URL url = Resources.getResource(seedDefinitionsResourceClass, resourcePath);
    final String yamlString = Resources.toString(url, StandardCharsets.UTF_8);
    final JsonNode configList = Yamls.deserialize(yamlString);
    return MoreIterators.toList(configList.elements()).stream().collect(Collectors.toMap(
        json -> json.get(idName).asText(),
        json -> json));
  }

  /**
   * Merges the corresponding spec JSON into the definition JSON. This is necessary because specs are
   * stored in a separate resource file from definitions.
   *
   * @param definitionJson JSON of connector definition that is missing a spec
   * @param specConfigs map of docker image to JSON of docker image/connector spec pair
   * @return JSON of connector definition including the connector spec
   */
  private static JsonNode mergeSpecIntoDefinition(final JsonNode definitionJson, final Map<String, JsonNode> specConfigs) {
    final String dockerImage = DockerUtils.getTaggedImageName(
        definitionJson.get("dockerRepository").asText(),
        definitionJson.get("dockerImageTag").asText());
    final JsonNode specConfigJson = specConfigs.get(dockerImage);
    if (specConfigJson == null || specConfigJson.get(SPEC) == null) {
      throw new UnsupportedOperationException(String.format("There is no seed spec for docker image %s", dockerImage));
    }
    ((ObjectNode) definitionJson).set(SPEC, specConfigJson.get(SPEC));
    return definitionJson;
  }

  private static JsonNode addMissingFields(final JsonNode element) {
    return addMissingPublicField(addMissingCustomField(addMissingTombstoneField(element)));
  }

}
