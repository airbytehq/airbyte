/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.cli.Clis;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.CombinedConnectorCatalog;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DockerImageSpec;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

/**
 * Generates a combined representation of the connector catalog that includes Sources, Destinations
 * and their specs all in one. This connector catalog can then be served and loaded from a
 * RemoteDefinitionsProvider.
 */
public class CombinedConnectorCatalogGenerator {

  private static final Option SEED_ROOT_OPTION = Option.builder("s").longOpt("seed-root").hasArg(true).required(true)
      .desc("path to where seed resource files are stored").build();
  private static final Option OUTPUT_FILENAME_OPTION = Option.builder("o").longOpt("output-filename").hasArg(true).required(true)
      .desc("name for the generated catalog json file").build();
  private static final Options OPTIONS = new Options().addOption(SEED_ROOT_OPTION).addOption(OUTPUT_FILENAME_OPTION);

  public static void main(final String[] args) throws Exception {
    final CommandLine parsed = Clis.parse(args, OPTIONS);
    final Path outputRoot = Path.of(parsed.getOptionValue(SEED_ROOT_OPTION.getOpt()));
    final String outputFileName = parsed.getOptionValue(OUTPUT_FILENAME_OPTION.getOpt());

    final CombinedConnectorCatalogGenerator combinedConnectorCatalogGenerator = new CombinedConnectorCatalogGenerator();
    combinedConnectorCatalogGenerator.run(outputRoot, outputFileName);
  }

  public void run(final Path outputRoot, final String outputFileName) {
    final List<JsonNode> destinationDefinitionsJson = getSeedJson(outputRoot, SeedConnectorType.DESTINATION.getDefinitionFileName());
    final List<JsonNode> destinationSpecsJson = getSeedJson(outputRoot, SeedConnectorType.DESTINATION.getSpecFileName());
    final List<JsonNode> sourceDefinitionsJson = getSeedJson(outputRoot, SeedConnectorType.SOURCE.getDefinitionFileName());
    final List<JsonNode> sourceSpecsJson = getSeedJson(outputRoot, SeedConnectorType.SOURCE.getSpecFileName());

    mergeSpecsIntoDefinitions(destinationDefinitionsJson, destinationSpecsJson, ConfigSchema.STANDARD_DESTINATION_DEFINITION);
    mergeSpecsIntoDefinitions(sourceDefinitionsJson, sourceSpecsJson, ConfigSchema.STANDARD_SOURCE_DEFINITION);

    final CombinedConnectorCatalog combinedCatalog = new CombinedConnectorCatalog()
        .withDestinations(destinationDefinitionsJson.stream().map(j -> Jsons.object(j, StandardDestinationDefinition.class)).toList())
        .withSources(sourceDefinitionsJson.stream().map(j -> Jsons.object(j, StandardSourceDefinition.class)).toList());

    IOs.writeFile(outputRoot.resolve(outputFileName), Jsons.toPrettyString(Jsons.jsonNode(combinedCatalog)));
  }

  private List<JsonNode> getSeedJson(final Path root, final String fileName) {
    final String jsonString = IOs.readFile(root, fileName);
    return MoreIterators.toList(Yamls.deserialize(jsonString).elements());
  }

  /**
   * Updates all connector definitions with provided specs.
   *
   * @param definitions - List of Source or Destination Definitions as generated in the seed files
   * @param specs - List of connector specs as generated in the seed files (see
   *        {@link DockerImageSpec})
   */
  @VisibleForTesting
  void mergeSpecsIntoDefinitions(final List<JsonNode> definitions, final List<JsonNode> specs, final ConfigSchema configSchema) {
    final Map<String, JsonNode> specsByImage = specs.stream().collect(Collectors.toMap(
        json -> json.get("dockerImage").asText(),
        json -> json.get("spec")));

    for (final JsonNode definition : definitions) {
      final String dockerImage = DockerUtils.getTaggedImageName(
          definition.get("dockerRepository").asText(),
          definition.get("dockerImageTag").asText());
      final JsonNode specConfigJson = specsByImage.get(dockerImage);

      if (specConfigJson == null) {
        throw new UnsupportedOperationException(String.format("A spec for docker image %s was not found", dockerImage));
      }

      ((ObjectNode) definition).set("spec", specConfigJson);

      if (!definition.hasNonNull("public")) {
        // All definitions in the catalog are public by default
        ((ObjectNode) definition).set("public", BooleanNode.TRUE);
      }

      AirbyteConfigValidator.AIRBYTE_CONFIG_VALIDATOR.ensureAsRuntime(configSchema, definition);
    }

  }

}
