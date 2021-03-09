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

package io.airbyte.config.init;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.helpers.YamlListToStandardDefinitions;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Collectors;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

/**
 * This class takes in a yaml file with a list of objects. It then then assigns each object a uuid
 * based on its name attribute. The uuid is written as a field in the object with the key specified
 * as the id-name. It then writes each object to its own file in the specified output directory.
 * Each file's name is the generated uuid. The goal is that a user should be able to add objects to
 * the database seed without having to generate uuids themselves. The output files should be
 * compatible with our file system database (config persistence).
 */
public class SeedRepository {

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

  private static CommandLine parse(final String[] args) {
    final CommandLineParser parser = new DefaultParser();
    final HelpFormatter helpFormatter = new HelpFormatter();

    try {
      return parser.parse(OPTIONS, args);
    } catch (final ParseException e) {
      helpFormatter.printHelp("", OPTIONS);
      throw new IllegalArgumentException(e);
    }
  }

  public static void main(final String[] args) throws IOException {
    final CommandLine parsed = parse(args);
    final String idName = parsed.getOptionValue(ID_NAME_OPTION.getOpt());
    final Path inputPath = Path.of(parsed.getOptionValue(INPUT_PATH_OPTION.getOpt()));
    final Path outputPath = Path.of(parsed.getOptionValue(OUTPUT_PATH_OPTION.getOpt()));

    new SeedRepository().run(idName, inputPath, outputPath);
  }

  public void run(final String idName, final Path input, final Path output) throws IOException {
    final var jsonNode = YamlListToStandardDefinitions.verifyAndConvertToJsonNode(idName, IOs.readFile(input));
    final var elementsIter = jsonNode.elements();

    // clean output directory.
    for (final Path file : Files.list(output).collect(Collectors.toList())) {
      Files.delete(file);
    }

    // write to output directory.
    while (elementsIter.hasNext()) {
      final JsonNode element = Jsons.clone(elementsIter.next());
      IOs.writeFile(
          output,
          element.get(idName).asText() + ".json",
          Jsons.toPrettyString(element));
    }
  }

}
