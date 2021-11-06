/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import java.util.HashMap;
import java.util.Map;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;

public class MdcScopeTest {

  private static final Map<String, String> originalMap = new HashMap<>() {

    {
      put("test", "entry");
      put("testOverride", "should be overrided");
    }

  };

  private static final Map<String, String> modificationInMDC = new HashMap<>() {

    {
      put("new", "will be added");
      put("testOverride", "will override");
    }

  };

  @BeforeEach
  public void init() {
    MDC.setContextMap(originalMap);
  }

  @Test
  @DisplayName("The MDC context is properly overrided")
  public void testMDCModified() {
    try (final MdcScope mdcScope = new MdcScope(modificationInMDC)) {
      final Map<String, String> mdcState = MDC.getCopyOfContextMap();

      Assertions.assertThat(mdcState).containsExactlyInAnyOrderEntriesOf(
          new HashMap<String, String>() {

            {
              put("test", "entry");
              put("new", "will be added");
              put("testOverride", "will override");
            }

          });

    }
  }

  @Test
  @DisplayName("The MDC context is properly restored")
  public void testMDCRestore() {
    try (final MdcScope mdcScope = new MdcScope(modificationInMDC)) {}

    final Map<String, String> mdcState = MDC.getCopyOfContextMap();

    Assertions.assertThat(mdcState).containsAllEntriesOf(originalMap);
    Assertions.assertThat(mdcState).doesNotContainKey("new");
  }

}
