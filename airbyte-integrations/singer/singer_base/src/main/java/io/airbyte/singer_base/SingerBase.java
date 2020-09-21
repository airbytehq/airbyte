package io.airbyte.singer_base;

import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
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

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class SingerBase {
  private static final Logger LOGGER = LoggerFactory.getLogger(SingerBase.class);
  private static final String SINGER_EXECUTABLE = "SINGER_EXECUTABLE";

  private enum Command {
    SPEC, CHECK, DISCOVER, READ, WRITE
  }

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

  public void run(final String[] args) throws IOException {
    final Command command = parseCommand(args);
    final Map<String, String> options = parseOptions(args, command);
    final Map<String, String> newOptions = transformInput(options); // mapping from airbyte to singer structs, field mapping, etc.
    final String newArgs = toCli(newOptions);

    final String singerExecutable = System.getenv(SINGER_EXECUTABLE);
    Preconditions.checkNotNull(singerExecutable, SINGER_EXECUTABLE + " environment variable cannot be null.");

    final String cmd = singerExecutable + newArgs;
    final ProcessBuilder processBuilder = new ProcessBuilder(cmd);
    final Process process = processBuilder.start();

    transformOutput(process.getInputStream(), options); // mapping from singer structs back to airbyte and then pipe to stdout.
  }

  private static String toCli(Map<String, String> newArgs) {
    return newArgs.entrySet().stream().map(entry -> "--" + entry.getKey() + (entry.getValue() != null ? " " + entry.getValue() : ""))
        .collect(Collectors.joining(" "));
  }

  // no-op for now.
  private Map<String, String> transformInput(Map<String, String> parsedArgs) {
    return parsedArgs;
  }

  // no-op for now.
  private void transformOutput(InputStream inputStream, Map<String, String> parsedArgs) throws IOException {
    int ch;
    while ((ch = inputStream.read()) != -1)
      System.out.write(ch);
    System.out.flush();
  }

  private static Command parseCommand(String[] args) {
    final CommandLineParser parser = new RelaxedParser();
    final HelpFormatter helpFormatter = new HelpFormatter();

    final Options options = new Options();
    options.addOptionGroup(commandGroup);

    try {
      final CommandLine parsed = parser.parse(options, args);
      return Command.valueOf(parsed.getOptions()[0].getLongOpt().toUpperCase());
      // if discover, then validate, etc...
    } catch (ParseException e) {
      LOGGER.error(e.toString());
      helpFormatter.printHelp("singer-base", options);
      throw new IllegalArgumentException();
    }
  }

  private static Map<String, String> parseOptions(String[] args, Command command) {
    final CommandLineParser parser = new DefaultParser();
    final HelpFormatter helpFormatter = new HelpFormatter();

    final Options options = new Options();
    options.addOptionGroup(commandGroup); // so that the parser does not throw an exception when encounter command args.

    if (command.equals(Command.CHECK)) {
      options.addOption(Option.builder().longOpt("config").desc("path to the json configuration file").hasArg(true).required(true).build());
    }

    if (command.equals(Command.DISCOVER)) {
      options.addOption(Option.builder().longOpt("config").desc("path to the json configuration file").hasArg(true).required(true).build());
      options.addOption(Option.builder().longOpt("schema").desc("output path for the discovered schema").hasArg(true).build());
    }

    if (command.equals(Command.READ)) {
      options.addOption(Option.builder().longOpt("config").desc("path to the json configuration file").hasArg(true).required(true).build());
      options.addOption(Option.builder().longOpt("schema").desc("input path for the schema").hasArg(true).build());
      options.addOption(Option.builder().longOpt("state").desc("path to the json-encoded state file").hasArg(true).build());
    }

    if (command.equals(Command.READ)) {
      options.addOption(Option.builder().longOpt("config").desc("path to the json configuration file").hasArg(true).required(true).build());
    }

    try {
      final CommandLine parse = parser.parse(options, args);
      return Arrays.stream(parse.getOptions()).collect(Collectors.toMap(Option::getLongOpt, Option::getValue));
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

  public static void main(String[] args) throws IOException {
    new SingerBase().run(args);
  }
}
