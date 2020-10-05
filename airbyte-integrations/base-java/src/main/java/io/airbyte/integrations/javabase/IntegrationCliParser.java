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

package io.airbyte.integrations.javabase;

import com.google.common.base.Preconditions;
import java.io.IOException;
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

/**
 * Parses command line args to a type safe config object for each command type.
 */
public class IntegrationCliParser {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationCliParser.class);

  private static final OptionGroup commandGroup = new OptionGroup();

  static {
    commandGroup.setRequired(true);
    commandGroup.addOption(Option.builder()
        .longOpt(Command.SPEC.toString().toLowerCase())
        .desc("outputs the json configuration specification")
        .build());
    commandGroup.addOption(Option.builder()
        .longOpt(Command.CHECK.toString().toLowerCase())
        .desc("checks the config can be used to connect")
        .build());
    commandGroup.addOption(Option.builder()
        .longOpt(Command.DISCOVER.toString().toLowerCase())
        .desc("outputs a catalog describing the source's schema")
        .build());
    commandGroup.addOption(Option.builder()
        .longOpt(Command.READ.toString().toLowerCase())
        .desc("reads the source and outputs messages to STDOUT")
        .build());
    commandGroup.addOption(Option.builder()
        .longOpt(Command.WRITE.toString().toLowerCase())
        .desc("writes messages from STDIN to the integration")
        .build());
  }

  public IntegrationConfig parse(final String[] args) throws IOException {
    final Command command = parseCommand(args);
    return parseOptions(args, command);
  }

  private static Command parseCommand(String[] args) throws IOException {
    final CommandLineParser parser = new RelaxedParser();
    final HelpFormatter helpFormatter = new HelpFormatter();

    final Options options = new Options();
    options.addOptionGroup(commandGroup);

    try {
      final CommandLine parsed = parser.parse(options, args);
      return Command.valueOf(parsed.getOptions()[0].getLongOpt().toUpperCase());
      // if discover, then validate, etc...
    } catch (ParseException e) {
      helpFormatter.printHelp("java-base", options);
      throw new IOException(e);
    }
  }

  private static IntegrationConfig parseOptions(String[] args, Command command) {

    final Options options = new Options();
    options.addOptionGroup(commandGroup); // so that the parser does not throw an exception when encounter command args.

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
            .builder().longOpt(JavaBaseConstants.ARGS_SCHEMA_KEY).desc(JavaBaseConstants.ARGS_SCHEMA_DESC).hasArg(true).build());
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_STATE_KEY).desc(JavaBaseConstants.ARGS_PATH_DESC).hasArg(true).build());
      }
      case WRITE -> {
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_CONFIG_KEY).desc(JavaBaseConstants.ARGS_CONFIG_DESC).hasArg(true).required(true).build());
        options.addOption(Option
            .builder().longOpt(JavaBaseConstants.ARGS_SCHEMA_KEY).desc(JavaBaseConstants.ARGS_SCHEMA_DESC).hasArg(true).build());
      }
      default -> throw new IllegalStateException("Unexpected value: " + command);
    }

    final CommandLine parsed = runParse(options, args, command);
    Preconditions.checkNotNull(parsed);
    final Map<String, String> argsMap = new HashMap<>();
    for (final Option option : parsed.getOptions()) {
      argsMap.put(option.getLongOpt(), option.getValue());
    }

    switch (command) {
      case SPEC -> {
        return IntegrationConfig.spec();
      }
      case CHECK -> {
        return IntegrationConfig.check(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY));
      }
      case DISCOVER -> {
        return IntegrationConfig.discover(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY));
      }
      case READ -> {
        return IntegrationConfig.read(
            argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY),
            argsMap.get(JavaBaseConstants.ARGS_SCHEMA_KEY),
            argsMap.get(JavaBaseConstants.ARGS_STATE_KEY));
      }
      case WRITE -> {
        return IntegrationConfig.write(
            argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY),
            argsMap.get(JavaBaseConstants.ARGS_SCHEMA_KEY));
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
      LOGGER.error(e.toString());
      helpFormatter.printHelp(command.toString().toLowerCase(), options);
      return null;
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
