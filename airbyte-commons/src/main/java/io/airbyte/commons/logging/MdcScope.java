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
 *      new HashMap&lt;String, String&gt;() {{
 *        put("my", "value");
 *      }}
 *     )) {
 *        ...
 *     }
 *   </code>
 * </pre>
 */
public class MdcScope implements AutoCloseable {

  public final static MdcScope.Builder DEFAULT_BUILDER = new Builder();

  private final Map<String, String> originalContextMap;

  public MdcScope(final Map<String, String> keyValuesToAdd) {
    originalContextMap = MDC.getCopyOfContextMap();

    keyValuesToAdd.forEach(
        (key, value) -> MDC.put(key, value));
  }

  @Override
  public void close() {
    MDC.setContextMap(originalContextMap);
  }

  public static class Builder {

    private Optional<String> maybeLogPrefix = Optional.empty();
    private Optional<Color> maybePrefixColor = Optional.empty();

    public Builder setLogPrefix(final String logPrefix) {
      this.maybeLogPrefix = Optional.ofNullable(logPrefix);

      return this;
    }

    public Builder setPrefixColor(final Color color) {
      this.maybePrefixColor = Optional.ofNullable(color);

      return this;
    }

    public MdcScope build() {
      final Map<String, String> extraMdcEntries = new HashMap<>();

      maybeLogPrefix.stream().forEach(logPrefix -> {
        final String potentiallyColoredLog = maybePrefixColor
            .map(color -> LoggingHelper.applyColor(color, logPrefix))
            .orElse(logPrefix);

        extraMdcEntries.put(LoggingHelper.LOG_SOURCE_MDC_KEY, potentiallyColoredLog);
      });

      return new MdcScope(extraMdcEntries);
    }

  }

}
