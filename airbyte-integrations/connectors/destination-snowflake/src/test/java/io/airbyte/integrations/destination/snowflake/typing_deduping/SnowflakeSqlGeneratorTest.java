/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import org.junit.jupiter.api.Test;

public class SnowflakeSqlGeneratorTest {

  private final SnowflakeSqlGenerator generator = new SnowflakeSqlGenerator();

  @Test
  void columnNameSpecialCharacterHandling() {
    assertAll(
        // If a ${ is present, then we should replace all of $, {, and } with underscores
        () -> assertEquals(
            new ColumnId(
                "__FOO_",
                "${foo}",
                "${FOO}"),
            generator.buildColumnId("${foo}")),
        // But normally, we should leave those characters untouched.
        () -> assertEquals(
            new ColumnId(
                "{FO$O}",
                "{fo$o}",
                "{FO$O}"),
            generator.buildColumnId("{fo$o}")));
  }

  /**
   * Similar to {@link #columnNameSpecialCharacterHandling()}, but for stream name/namespace
   */
  @Test
  void streamNameSpecialCharacterHandling() {
    assertAll(
        () -> assertEquals(
            new StreamId(
                "__FOO_",
                "__BAR_",
                "airbyte_internal",
                "__foo__raw__stream___bar_",
                "${foo}",
                "${bar}"),
            generator.buildStreamId("${foo}", "${bar}", "airbyte_internal")),
        () -> assertEquals(
            new StreamId(
                "{FO$O}",
                "{BA$R}",
                "airbyte_internal",
                "{fo$o}_raw__stream_{ba$r}",
                "{fo$o}",
                "{ba$r}"),
            generator.buildStreamId("{fo$o}", "{ba$r}", "airbyte_internal")));
  }

}
