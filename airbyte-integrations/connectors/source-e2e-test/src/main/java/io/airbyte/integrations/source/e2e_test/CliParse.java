/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.e2e_test;

import com.google.common.base.Preconditions;
import io.airbyte.cdk.integrations.base.Command;
import io.airbyte.cdk.integrations.base.IntegrationConfig;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.cli.Clis;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;

// todo (cgardens) - use argparse4j.github.io instead of org.apache.commons.cli to leverage better
// sub-parser support.
/**
 * Parses command line args to a type safe config object for each command type.
 */
public class CliParse {

  private static final OptionGroup COMMAND_GROUP;

  static {
    OptionGroup optionGroup = new OptionGroup();
    optionGroup.setRequired(true);

    optionGroup.addOption(
        Option.builder()
            .longOpt(Command.SPEC.toString().toLowerCase(Locale.getDefault()))
            .desc("outputs the json configuration specification")
            .build());
    optionGroup.addOption(
        Option.builder()
            .longOpt(Command.CHECK.toString().toLowerCase(Locale.getDefault()))
            .desc("checks the config can be used to connect")
            .build());
    optionGroup.addOption(
        Option.builder()
            .longOpt(Command.DISCOVER.toString().toLowerCase(Locale.getDefault()))
            .desc("outputs a catalog describing the source's catalog")
            .build());
    optionGroup.addOption(
        Option.builder()
            .longOpt(Command.READ.toString().toLowerCase(Locale.getDefault()))
            .desc("reads the source and outputs messages to STDOUT")
            .build());
    optionGroup.addOption(
        Option.builder()
            .longOpt(Command.WRITE.toString().toLowerCase(Locale.getDefault()))
            .desc("writes messages from STDIN to the integration")
            .build());

    COMMAND_GROUP = optionGroup;
  }

  public IntegrationConfig parse(String[] args) {
    Command command = parseCommand(args);
    return parseOptions(args, command);
  }

  private static Command parseCommand(String[] args) {
    Options options = new Options();
    options.addOptionGroup(COMMAND_GROUP);

    CommandLine parsed = Clis.parse(args, options, Clis.getRelaxedParser());
    return Command.valueOf(parsed.getOptions()[0].getLongOpt().toUpperCase(Locale.getDefault()));
  }

  private static IntegrationConfig parseOptions(String[] args, Command command) {
    Options options = new Options();
    options.addOptionGroup(
        COMMAND_GROUP); // so that the parser does not throw an exception when encounter command args.

    switch (command) {
      case SPEC:
        // no args.
        break;
      case CHECK:
      case DISCOVER:
        options.addOption(
            Option.builder()
                .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
                .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
                .hasArg(true)
                .required(true)
                .build());
        break;
      case READ:
        options.addOption(
            Option.builder()
                .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
                .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
                .hasArg(true)
                .required(true)
                .build());
        options.addOption(
            Option.builder()
                .longOpt(JavaBaseConstants.ARGS_CATALOG_KEY)
                .desc(JavaBaseConstants.ARGS_CATALOG_DESC)
                .hasArg(true)
                .build());
        options.addOption(
            Option.builder()
                .longOpt(JavaBaseConstants.ARGS_STATE_KEY)
                .desc(JavaBaseConstants.ARGS_PATH_DESC)
                .hasArg(true)
                .build());
        break;
      case WRITE:
        options.addOption(
            Option.builder()
                .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
                .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
                .hasArg(true)
                .required(true)
                .build());
        options.addOption(
            Option.builder()
                .longOpt(JavaBaseConstants.ARGS_CATALOG_KEY)
                .desc(JavaBaseConstants.ARGS_CATALOG_DESC)
                .hasArg(true)
                .build());
        break;
    }

    CommandLine parsed = Clis.parse(args, options, command.toString().toLowerCase(Locale.getDefault()));
    Preconditions.checkNotNull(parsed);
    Map<String, String> argsMap = new HashMap<>();
    for (Option option : parsed.getOptions()) {
      argsMap.put(option.getLongOpt(), option.getValue());
    }

    return switch (command) {
      case SPEC -> IntegrationConfig.spec();
      case CHECK -> IntegrationConfig.check(
          Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)));
      case DISCOVER -> IntegrationConfig.discover(
          Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)));
      case READ -> IntegrationConfig.read(
          Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)),
          Path.of(argsMap.get(JavaBaseConstants.ARGS_CATALOG_KEY)),
          argsMap.containsKey(JavaBaseConstants.ARGS_STATE_KEY)
              ? Path.of(argsMap.get(JavaBaseConstants.ARGS_STATE_KEY))
              : null);
      case WRITE -> IntegrationConfig.write(
          Path.of(argsMap.get(JavaBaseConstants.ARGS_CONFIG_KEY)),
          Path.of(argsMap.get(JavaBaseConstants.ARGS_CATALOG_KEY)));
    };
  }

}
