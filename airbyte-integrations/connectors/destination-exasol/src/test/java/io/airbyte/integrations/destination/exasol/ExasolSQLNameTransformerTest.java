/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class ExasolSQLNameTransformerTest {

  private ExasolSQLNameTransformer transformer;

  @BeforeEach
  void setUp() {
    transformer = new ExasolSQLNameTransformer();
  }

  @ParameterizedTest
  @CsvSource({"text, TEXT", "Text, TEXT", "TEXT, TEXT", "_äöüß, _ÄÖÜSS"})
  void applyDefaultCase(String input, String expectedOutput) {
    assertEquals(expectedOutput, transformer.applyDefaultCase(input));
  }

  @ParameterizedTest
  @CsvSource({"stream, \"_airbyte_raw_stream\"",
    "Stream, \"_airbyte_raw_Stream\"",
    "stream*, \"_airbyte_raw_stream_\"",
    "äöü, \"_airbyte_raw_aou\""})
  void getRawTableName(String streamName, String expectedTableName) {
    assertEquals(expectedTableName, transformer.getRawTableName(streamName));
  }

  @Test
  void getTmpTableNamePrefixSuffix() {
    String tmpTableName = transformer.getTmpTableName("stream");
    assertThat(tmpTableName, allOf(
        startsWith("\"_airbyte_tmp_"),
        endsWith("_stream\"")));
  }

  @Test
  void getTmpTableNameDifferentForEachCall() {
    String name1 = transformer.getTmpTableName("stream");
    String name2 = transformer.getTmpTableName("stream");
    assertThat(name1, not(equalTo(name2)));
  }

  @ParameterizedTest
  @CsvSource({"stream, stream",
    "Stream,     Stream",
    "STREAM,     STREAM",
    "stream*,    stream_",
    "_stream_,   _stream_",
    "äöü,        aou",
    "\"stream,   stream",
    "stream\",   stream",
    "\"stream\", stream",})
  void convertStreamName(String streamName, String expectedTableName) {
    assertThat(transformer.convertStreamName(streamName), equalTo("\"" + expectedTableName + "\""));
  }

}
