/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import io.airbyte.commons.logging.LoggingHelper.Color;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.MDC;

/**
 * This class is an autoClosable class that will add some specific values into the log MDC. When
 * being close, it will restore the orginal MDC. It is advise to use it like that:
 *
 * <pre>
 *   <code>
 *     try(final ScopedMDCChange scopedMDCChange = new ScopedMDCChange(
 *      new HashMap<String, String>() {{
 *        put("my", "value");
 *      }}
 *     )) {
 *        ...
 *     }
 *   </code>
 * </pre>
 */
public class MdcScope implements AutoCloseable {

  private final Map<String, String> originalContextMap;

  public MdcScope(final Map<String, String> keyValuesToAdd) {
    originalContextMap = MDC.getCopyOfContextMap();

    keyValuesToAdd.forEach(
        (key, value) -> MDC.put(key, value));
  }

  @Override
  public void close() throws Exception {
    MDC.setContextMap(originalContextMap);
  }

  public static class MdcScopeBuilder {

    private Optional<String> maybeLogPrefix = Optional.empty();
    private Optional<Color> maybePrefixColor = Optional.empty();

    public MdcScopeBuilder setLogPrefix(final String logPrefix) {
      this.maybeLogPrefix = Optional.ofNullable(logPrefix);

      return this;
    }

    public MdcScopeBuilder setPrefixColor(final Color color) {
      this.maybePrefixColor = Optional.ofNullable(color);

      return this;
    }

    public MdcScope build() {
      final Map<String, String> extraMdcEntries = new HashMap<>();

      maybeLogPrefix.map(logPrefix -> extraMdcEntries.put(LoggingHelper.LOG_SOURCE_MDC_KEY, LoggingHelper.applyColor(Color.GREEN, logPrefix)));

      return new MdcScope(extraMdcEntries);
    }

  }

}
