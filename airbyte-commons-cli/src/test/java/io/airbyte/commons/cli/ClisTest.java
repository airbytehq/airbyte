/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.cli;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.junit.jupiter.api.Test;

class ClisTest {

  private static final String ALPHA = "alpha";
  private static final String BETA = "beta";

  @Test
  void testCreateOptionGroup() {
    final Option optionA = new Option("a", ALPHA);
    final Option optionB = new Option("b", BETA);
    final OptionGroup optionGroupExpected = new OptionGroup();
    optionGroupExpected.addOption(optionA);
    optionGroupExpected.addOption(optionB);

    final OptionGroup optionGroupActual = Clis.createOptionGroup(
        false,
        optionA,
        optionB);

    // hack: OptionGroup does not define hashcode, so compare its string instead of the object itself.
    assertEquals(optionGroupExpected.toString(), optionGroupActual.toString());
  }

  @Test
  void testParse() {
    final Option optionA = Option.builder("a").required(true).hasArg(true).build();
    final Option optionB = Option.builder("b").required(true).hasArg(true).build();
    final Options options = new Options().addOption(optionA).addOption(optionB);
    final String[] args = {"-a", ALPHA, "-b", BETA};
    final CommandLine parsed = Clis.parse(args, options, new DefaultParser());
    assertEquals(ALPHA, parsed.getOptions()[0].getValue());
    assertEquals(BETA, parsed.getOptions()[1].getValue());
  }

  @Test
  void testParseNonConforming() {
    final Option optionA = Option.builder("a").required(true).hasArg(true).build();
    final Option optionB = Option.builder("b").required(true).hasArg(true).build();
    final Options options = new Options().addOption(optionA).addOption(optionB);
    final String[] args = {"-a", ALPHA, "-b", BETA, "-c", "charlie"};
    assertThrows(IllegalArgumentException.class, () -> Clis.parse(args, options, new DefaultParser()));
  }

  @Test
  void testParseNonConformingWithSyntax() {
    final Option optionA = Option.builder("a").required(true).hasArg(true).build();
    final Option optionB = Option.builder("b").required(true).hasArg(true).build();
    final Options options = new Options().addOption(optionA).addOption(optionB);
    final String[] args = {"-a", ALPHA, "-b", BETA, "-c", "charlie"};
    assertThrows(IllegalArgumentException.class, () -> Clis.parse(args, options, new DefaultParser(), "search"));
  }

  @Test
  void testRelaxedParser() {
    final Option optionA = Option.builder("a").required(true).hasArg(true).build();
    final Option optionB = Option.builder("b").required(true).hasArg(true).build();
    final Options options = new Options().addOption(optionA).addOption(optionB);
    final String[] args = {"-a", ALPHA, "-b", BETA, "-c", "charlie"};
    final CommandLine parsed = Clis.parse(args, options, Clis.getRelaxedParser());
    assertEquals(ALPHA, parsed.getOptions()[0].getValue());
    assertEquals(BETA, parsed.getOptions()[1].getValue());
  }

}
