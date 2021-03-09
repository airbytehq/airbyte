package io.airbyte.integrations.acceptance_tests.source;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.acceptance_tests.source.models.SourceAcceptanceTestInputs;
import io.airbyte.integrations.acceptance_tests.source.utils.TestRunner;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;

public class FileBasedSourceAcceptanceTestDriver {
  private static SourceAcceptanceTestInputs parseArguments(String[] args) throws IOException {
    ArgumentParser parser = ArgumentParsers.newFor(FileBasedSourceAcceptanceTestDriver.class.getName()).build()
        .defaultHelp(true)
        .description("Run source acceptance tests");

    parser.addArgument("--testConfig")
        .required(true)
        .help("Path to the source acceptance test input configuration");

    Namespace ns = null;
    try {
      ns = parser.parseArgs(args);
    } catch (ArgumentParserException e) {
      throw new IllegalArgumentException(e);
    }

    String testConfigPath = ns.getString("testConfig");

    String testConfig = Files.readString(Path.of(testConfigPath));
    return Jsons.deserialize(testConfig, SourceAcceptanceTestInputs.class);
  }

  public static void main(String[] args) throws IOException {
    SourceAcceptanceTestInputs testInputs = parseArguments(args);
    // transform into inputs for the various test classes
    // run each test class
    ArrayList<Class<?>> classes =
        Lists.newArrayList(CoreAcceptanceTestRunner.class, FullRefreshAcceptanceTestRunner.class, IncrementalAcceptanceTestRunner.class);

    for (Class<?> aClass : classes) {
      TestRunner.runTestClass(aClass);
    }
  }

}
