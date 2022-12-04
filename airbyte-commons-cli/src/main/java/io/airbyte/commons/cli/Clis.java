/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.cli;

import java.util.ArrayList;
import java.util.List;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

public class Clis {

  /**
   * Parse an options object
   *
   * @param args - command line args
   * @param options - expected options
   * @return object with parsed values.
   */
  public static CommandLine parse(final String[] args, final Options options, final CommandLineParser parser, final String commandLineSyntax) {
    final HelpFormatter helpFormatter = new HelpFormatter();

    try {
      return parser.parse(options, args);
    } catch (final ParseException e) {
      if (commandLineSyntax != null && !commandLineSyntax.isEmpty()) {
        helpFormatter.printHelp(commandLineSyntax, options);
      }
      throw new IllegalArgumentException(e);
    }
  }

  public static CommandLine parse(final String[] args, final Options options, final String commandLineSyntax) {
    return parse(args, options, new DefaultParser(), commandLineSyntax);
  }

  public static CommandLine parse(final String[] args, final Options options, final CommandLineParser parser) {
    return parse(args, options, parser, null);
  }

  public static CommandLine parse(final String[] args, final Options options) {
    return parse(args, options, new DefaultParser());
  }

  /**
   * Provide a fluent interface for building an OptionsGroup.
   *
   * @param isRequired - is the option group required
   * @param options - options in the option group
   * @return the created option group.
   */
  public static OptionGroup createOptionGroup(final boolean isRequired, final Option... options) {
    final OptionGroup optionGroup = new OptionGroup();
    optionGroup.setRequired(isRequired);
    for (final Option option : options) {
      optionGroup.addOption(option);
    }
    return optionGroup;
  }

  public static CommandLineParser getRelaxedParser() {
    return new RelaxedParser();
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
