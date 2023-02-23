/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.cli.Clis;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.yaml.Yamls;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

public class ConnectorMarkdownGenerator {

  private static final Option PROJECT_ROOT_OPTION = Option.builder("p").longOpt("project-root").hasArg(true).required(true)
      .desc("path to where seed resource files are stored").build();

  private static final Option SEED_ROOT_OPTION = Option.builder("s").longOpt("seed-root").hasArg(true).required(true)
      .desc("path to where seed resource files are stored").build();
  private static final Option OUTPUT_FILENAME_OPTION = Option.builder("o").longOpt("output-filename").hasArg(true).required(true)
      .desc("name for the generated catalog json file").build();
  private static final Options OPTIONS = new Options().addOption(PROJECT_ROOT_OPTION).addOption(SEED_ROOT_OPTION).addOption(OUTPUT_FILENAME_OPTION);

  private static final String githubCodeBase = "https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors";
  private static final String githubIconBase =
      "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/icons";
  private static final String iconSize = "30";

  public static void main(final String[] args) throws Exception {
    final CommandLine parsed = Clis.parse(args, OPTIONS);
    final Path outputRoot = Path.of(parsed.getOptionValue(PROJECT_ROOT_OPTION.getOpt()));
    final Path seedRoot = Path.of(parsed.getOptionValue(SEED_ROOT_OPTION.getOpt()));
    final String outputFileName = parsed.getOptionValue(OUTPUT_FILENAME_OPTION.getOpt());

    final ConnectorMarkdownGenerator mdGenerator = new ConnectorMarkdownGenerator();
    mdGenerator.run(outputRoot, seedRoot, outputFileName);
  }

  public void run(final Path outputRoot, final Path seedRoot, final String outputFileName) {
    final List<JsonNode> destinationDefinitionsJson = getSeedJson(seedRoot, SeedConnectorType.DESTINATION.getDefinitionFileName());
    final List<JsonNode> sourceDefinitionsJson = getSeedJson(seedRoot, SeedConnectorType.SOURCE.getDefinitionFileName());
    String body = buildMarkdown(sourceDefinitionsJson, destinationDefinitionsJson);
    IOs.writeFile(outputRoot.resolve(outputFileName), body);
  }

  private List<JsonNode> getSeedJson(final Path root, final String fileName) {
    final String jsonString = IOs.readFile(root, fileName);
    return MoreIterators.toList(Yamls.deserialize(jsonString).elements())
        .stream()
        .sorted(Comparator.comparing(o -> o.get("name").asText()))
        .toList();
  }

  private String buildMarkdown(List<JsonNode> sourceDefinitionsJson, List<JsonNode> destinationDefinitionsJson) {
    final List<String> bodyParts = new ArrayList<>();

    bodyParts.add("# Airbyte Connectors");

    bodyParts.add("");
    bodyParts.add("## Sources");
    bodyParts.add("");
    bodyParts.add(buildMarkdownTable(sourceDefinitionsJson, "Source"));

    bodyParts.add("");
    bodyParts.add("## Destinations");
    bodyParts.add("");
    bodyParts.add(buildMarkdownTable(destinationDefinitionsJson, "Destination"));

    return String.join("\r\n", bodyParts);
  }

  @SuppressWarnings("PMD")
  private String buildMarkdownTable(List<JsonNode> definitions, String type) {
    final List<String> bodyParts = new ArrayList<>();

    List<String> headers = new ArrayList<>();
    headers.add("Name");
    headers.add("Icon");
    headers.add("Type");
    headers.add("Image");
    headers.add("Release Stage");
    headers.add("Docs");
    headers.add("Code");
    headers.add("ID");

    bodyParts.add("| " + String.join(" | ", headers) + " |");
    bodyParts.add("|----|----|----|----|----|----|----|----|");
    for (final JsonNode definition : definitions) {
      final String name = definition.get("name").asText();
      final String codeName = definition.get("dockerRepository").asText().split("/")[1];
      final String icon = definition.get("icon") != null ? definition.get("icon").asText() : "";
      final String iconLink = !icon.equals("")
          ? "<img alt=\"" + name + " icon\" src=\"" + githubIconBase + "/" + icon + "\" height=\"" + iconSize + "\" height=\"" + iconSize + "\"/>"
          : "x";
      final String dockerImage = definition.get("dockerRepository").asText() + ":" + definition.get("dockerImageTag").asText();
      final String releaseStage = definition.get("releaseStage") != null ? definition.get("releaseStage").asText() : "unknown";
      final String documentationUrl = definition.get("documentationUrl") != null ? definition.get("documentationUrl").asText() : "";
      final String docLink = !documentationUrl.equals("") ? "[link](" + documentationUrl + ")" : "missing";
      final String codeLink = "[code](" + githubCodeBase + "/" + codeName + ")";
      final String id = "<small>`" + definition.get(type.toLowerCase() + "DefinitionId").asText() + "`</small>";

      bodyParts.add("| **" + name + "** | " + iconLink + " | " + type + " | " + dockerImage + " | " + releaseStage + " | " + docLink + " | "
          + codeLink + " | " + id + " |");
    }

    return String.join("\r\n", bodyParts);
  }

}
