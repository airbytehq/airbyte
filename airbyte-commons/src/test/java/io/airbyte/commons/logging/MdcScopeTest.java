/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import java.util.Map;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;

class MdcScopeTest {

  private static final Map<String, String> originalMap = Map.of("test", "entry", "testOverride", "should be overrided");

  private static final Map<String, String> modificationInMDC = Map.of("new", "will be added", "testOverride", "will override");

  @BeforeEach
  void init() {
    MDC.setContextMap(originalMap);
  }

  @Test
  @DisplayName("The MDC context is properly overrided")
  void testMDCModified() {
    try (final MdcScope ignored = new MdcScope(modificationInMDC)) {
      final Map<String, String> mdcState = MDC.getCopyOfContextMap();

      Assertions.assertThat(mdcState).containsExactlyInAnyOrderEntriesOf(
          Map.of("test", "entry", "new", "will be added", "testOverride", "will override"));
    }
  }

  @Test
  @DisplayName("The MDC context is properly restored")
  void testMDCRestore() {
    try (final MdcScope ignored = new MdcScope(modificationInMDC)) {}

    final Map<String, String> mdcState = MDC.getCopyOfContextMap();

    Assertions.assertThat(mdcState).containsAllEntriesOf(originalMap);
    Assertions.assertThat(mdcState).doesNotContainKey("new");
  }

}
