/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.google.common.base.Preconditions;
import io.airbyte.commons.cli.Clis;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// todo (cgardens) - use argparse4j.github.io instead of org.apache.commons.cli to leverage better
// sub-parser support.
/**
 * Parses command line args to a type safe config object for each command type.
 */
public class IntegrationCliParser {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationCliParser.class);

  private static final OptionGroup COMMAND_GROUP = Clis.createOptionGroup(
      true,
      Option.builder()
          .longOpt(Command.SPEC.toString().toLowerCase())
          .desc("outputs the json configuration specification")
          .build(),
      Option.builder()
          .longOpt(Command.CHECK.toString().toLowerCase())
          .desc("checks the config can be used to connect")
          .build(),
      Option.builder()
          .longOpt(Command.DISCOVER.toString().toLowerCase())
          .desc("outputs a catalog describing the source's catalog")
          .build(),
      Option.builder()
          .longOpt(Command.READ.toString().toLowerCase())
          .desc("reads the source and outputs messages to STDOUT")
          .build(),
      Option.builder()
          .longOpt(Command.WRITE.toString().toLowerCase())
          .desc("writes messages from STDIN to the integration")
          .build());

  public IntegrationConfig parse(final String[] args) {
    final Command command = parseCommand(args);
    return parseOptions(args, command);
  }

  private static Command parseCommand(final String[] args) {
    final Options options = new Options();
    options.addOptionGroup(COMMAND_GROUP);

    final CommandLine parsed = Clis.parse(args, options, Clis.getRelaxedParser());
    return Command.valueOf(parsed.getOptions()[0].getLongOpt().toUpperCase());
  }

  private static IntegrationConfig parseOptions(final String[] args, final Command command) {

    final Options options = new Options();
    options.addOptionGroup(COMMAND_GROUP); // so that the parser does not throw an exception when encounter command args.

    switch (command) {
      case SPEC -> {
        // no args.
      }
      case CHECK, DISCOVER -> options.addOption(Option.builder()
          .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
          .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
          .hasArg(true)
          .required(true)
          .build());
      case READ -> {
        options.addOption(Option.builder()
            .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
            .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
            .hasArg(true)
            .required(true)
            .build());
        options.addOption(Option.builder()
            .longOpt(JavaBaseConstants.ARGS_CATALOG_KEY)
            .desc(JavaBaseConstants.ARGS_CATALOG_DESC)
            .hasArg(true)
            .build());
        options.addOption(Option.builder()
            .longOpt(JavaBaseConstants.ARGS_STATE_KEY)
            .desc(JavaBaseConstants.ARGS_PATH_DESC)
            .hasArg(true)
            .build());
      }
      case WRITE -> {
        options.addOption(Option.builder()
            .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
            .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
            .hasArg(true)
            .required(true).build());
        options.addOption(Option.builder()
            .longOpt(JavaBaseConstants.ARGS_CATALOG_KEY)
            .desc(JavaBaseConstants.ARGS_CATALOG_DESC)
            .hasArg(true)
            .build());
      }
      default -> throw new IllegalStateException("Unexpected value: " + command);
    }

    final CommandLine parsed = Clis.parse(args, options, command.toString().toLowerCase());
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

}
