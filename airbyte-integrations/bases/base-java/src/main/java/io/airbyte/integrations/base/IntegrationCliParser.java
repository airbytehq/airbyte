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

package io.airbyte.integrations.base;

import com.google.common.base.Preconditions;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// todo (cgardens) - use argparse4j.github.io instead of org.apache.commons.cli to leverage better
// sub-parser support.
/**
 * Parses command line args to a type safe config object for each command type.
 */
public class IntegrationCliParser {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationCliParser.class);

  private static final OptionGroup COMMAND_GROUP = new OptionGroup();

  static {
    COMMAND_GROUP.setRequired(true);
    COMMAND_GROUP.addOption(Option.builder()
        .longOpt(Command.SPEC.toString().toLowerCase())
        .desc("outputs the json configuration specification")
        .build());
    COMMAND_GROUP.addOption(Option.builder()
        .longOpt(Command.CHECK.toString().toLowerCase())
        .desc("checks the config can be used to connect")
        .build());
    COMMAND_GROUP.addOption(Option.builder()
        .longOpt(Command.DISCOVER.toString().toLowerCase())
        .desc("outputs a catalog describing the source's catalog")
        .build());
    COMMAND_GROUP.addOption(Option.builder()
        .longOpt(Command.READ.toString().toLowerCase())
        .desc("reads the source and outputs messages to STDOUT")
        .build());
    COMMAND_GROUP.addOption(Option.builder()
        .longOpt(Command.WRITE.toString().toLowerCase())
        .desc("writes messages from STDIN to the integration")
        .build());
  }

  public IntegrationConfig parse(final String[] args) {
    final Command command = parseCommand(args);
    return parseOptions(args, command);
  }

  private static Command parseCommand(String[] args) {
    final CommandLineParser parser = new RelaxedParser();
    final HelpFormatter helpFormatter = new HelpFormatter();

    final Options options = new Options();
    options.addOptionGroup(COMMAND_GROUP);

    try {
      final CommandLine parsed = parser.parse(options, args);
      return Command.valueOf(parsed.getOptions()[0].getLongOpt().toUpperCase());
      // if discover, then validate, etc...
    } catch (ParseException e) {
      helpFormatter.printHelp("java-base", options);
      throw new IllegalArgumentException(e);
    }
  }

  private static IntegrationConfig parseOptions(String[] args, Command command) {

    final Options options = new Options();
    options.addOptionGroup(COMMAND_GROUP); // so that the parser does not throw an exception when encounter command args.

    switch (command) {
      case SPEC -> {
        // no args.
      }
      case CHECK, DISCOVER -> options.addOption(Option
          .builder().longOpt(JavaBaseConstants.ARGS_CONFIG_KEY).desc(JavaBaseConstants.ARGS_CONFIG_DESC).hasArg(true).required(true).build());
      case READ -> {
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_CONFIG_KEY).desc(JavaBaseConstants.ARGS_CONFIG_DESC).hasArg(true).required(true).build());
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_CATALOG_KEY).desc(JavaBaseConstants.ARGS_CATALOG_DESC).hasArg(true).build());
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_STATE_KEY).desc(JavaBaseConstants.ARGS_PATH_DESC).hasArg(true).build());
      }
      case WRITE -> {
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_CONFIG_KEY).desc(JavaBaseConstants.ARGS_CONFIG_DESC).hasArg(true).required(true).build());
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_CATALOG_KEY).desc(JavaBaseConstants.ARGS_CATALOG_DESC).hasArg(true).build());
      }
      default -> throw new IllegalStateException("Unexpected value: " + command);
    }

    final CommandLine parsed = runParse(options, args, command);
    Preconditions.checkNotNull(parsed);
    final Map<String, String> argsMap = new HashMap<>();
    for (final Option option : parsed.getOptions()) {
      argsMap.put(option.getLongOpt(), option.getValue());
    }
    LOGGER.info("integration args: {}", argsMap);

    switch (command) {
      case SPEC -> {
        return IntegrationConfig.spec();
      }
      case CHECK -> {
        return IntegrationConfig.check(Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)));
      }
      case DISCOVER -> {
        return IntegrationConfig.discover(Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)));
      }
      case READ -> {
        return IntegrationConfig.read(
            Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)),
            Path.of(argsMap.get(JavaBaseConstants.ARGS_CATALOG_KEY)),
            argsMap.containsKey(JavaBaseConstants.ARGS_STATE_KEY) ? Path.of(argsMap.get(JavaBaseConstants.ARGS_STATE_KEY)) : null);
      }
      case WRITE -> {
        return IntegrationConfig.write(
            Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)),
            Path.of(argsMap.get(JavaBaseConstants.ARGS_CATALOG_KEY)));
      }
      default -> throw new IllegalStateException("Unexpected value: " + command);
    }
  }

  private static CommandLine runParse(Options options, String[] args, Command command) {
    final CommandLineParser parser = new DefaultParser();
    final HelpFormatter helpFormatter = new HelpFormatter();

    try {
      return parser.parse(options, args);
    } catch (ParseException e) {
      helpFormatter.printHelp(command.toString().toLowerCase(), options);
      throw new IllegalArgumentException(e);
    }
  }

  // https://stackoverflow.com/questions/33874902/apache-commons-cli-1-3-1-how-to-ignore-unknown-arguments
  private static class RelaxedParser extends DefaultParser {

    @Override
    public CommandLine parse(final Options options, final String[] arguments) throws ParseException {
      final List<String> knownArgs = new ArrayList<>();
      for (int i = 0; i < arguments.length; i++) {
        if (options.hasOption(arguments[i])) {
          knownArgs.add(arguments[i]);
          if (i + 1 < arguments.length && options.getOption(arguments[i]).hasArg()) {
            knownArgs.add(arguments[i + 1]);
          }
        }
      }
      return super.parse(options, knownArgs.toArray(new String[0]));
    }

  }

}
