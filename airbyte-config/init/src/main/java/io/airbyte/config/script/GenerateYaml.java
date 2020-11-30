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

package io.airbyte.config.script;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

public class GenerateYaml {

  private static final Options OPTIONS = new Options();
  private static final Option ID_NAME_OPTION = new Option("id", "id-name", true, "field name of the id");
  private static final Option INPUT_PATH_OPTION = new Option("i", "input-path", true, "path to input file");
  private static final Option OUTPUT_PATH_OPTION = new Option("o", "output-path", true, "path to where files will be output");
  static {
    ID_NAME_OPTION.setRequired(true);
    INPUT_PATH_OPTION.setRequired(true);
    OUTPUT_PATH_OPTION.setRequired(true);
    OPTIONS.addOption(ID_NAME_OPTION);
    OPTIONS.addOption(INPUT_PATH_OPTION);
    OPTIONS.addOption(OUTPUT_PATH_OPTION);
  }

  public void run() throws IOException {
    final List<Path> collect = Files
        .list(Path.of("/Users/charles/code/airbyte/airbyte-config/init/src/main/resources/config/STANDARD_SOURCE_DEFINITION"))
        .collect(Collectors.toList());

    ArrayNode nodes = new ObjectMapper().createArrayNode();
    for (Path path : collect) {
      nodes.add(Jsons.deserialize(IOs.readFile(path)));
    }

    final ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

    IOs.writeFile(Path.of("/Users/charles/code/airbyte/airbyte-config/init/src/main/resources/seed/source_definitions.yaml"),
        mapper.writeValueAsString(nodes));

    // final JsonNode jsonNode = mapper.readTree(input.toFile());
    // final Iterator<JsonNode> elements = jsonNode.elements();
    // final Set<String> names = new HashSet<>();
    //
    // while (elements.hasNext()) {
    // final JsonNode element = Jsons.clone(elements.next());
    // final String name = element.get("name").asText();
    //
    // // validate the name is unique.
    // if (names.contains(name)) {
    // throw new IllegalArgumentException("Multiple records have the name: " + name);
    // }
    // names.add(name);
    //
    // final UUID uuid = UUID.nameUUIDFromBytes(name.getBytes(Charsets.UTF_8));
    // ((ObjectNode) element).put(idName, uuid.toString());
    //
    // IOs.writeFile(
    // output,
    // uuid.toString() + ".json",
    // element.toPrettyString()); // todo (cgardens) - adds obnoxious space in front of ":".
    // }
  }

  // private static CommandLine parse(String[] args) {
  // final CommandLineParser parser = new DefaultParser();
  // final HelpFormatter helpFormatter = new HelpFormatter();
  //
  // try {
  // return parser.parse(OPTIONS, args);
  // } catch (ParseException e) {
  // helpFormatter.printHelp("", OPTIONS);
  // throw new IllegalArgumentException(e);
  // }
  // }

  public static void main(String[] args) throws IOException {
    // final CommandLine parsed = parse(args);
    // final String idName = parsed.getOptionValue(ID_NAME_OPTION.getOpt());
    // final Path inputPath = Path.of(parsed.getOptionValue(INPUT_PATH_OPTION.getOpt()));
    // final Path outputPath = Path.of(parsed.getOptionValue(OUTPUT_PATH_OPTION.getOpt()));

    new GenerateYaml().run();
  }

}
