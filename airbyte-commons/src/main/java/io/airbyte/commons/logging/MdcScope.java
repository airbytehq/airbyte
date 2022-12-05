/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import io.airbyte.commons.logging.LoggingHelper.Color;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.MDC;

/**
 * This class is an autoClosable class that will add some specific values into the log MDC. When
 * being close, it will restore the original MDC. It is advised to use it like that:
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

    keyValuesToAdd.forEach(MDC::put);
  }

  @Override
  public void close() {
    MDC.setContextMap(originalContextMap);
  }

  public static class Builder {

    private Optional<String> maybeLogPrefix = Optional.empty();
    private Optional<Color> maybePrefixColor = Optional.empty();
    private boolean simple = true;

    public Builder setLogPrefix(final String logPrefix) {
      this.maybeLogPrefix = Optional.ofNullable(logPrefix);

      return this;
    }

    public Builder setPrefixColor(final Color color) {
      this.maybePrefixColor = Optional.ofNullable(color);

      return this;
    }

    // Use this to disable simple logging for things in an MdcScope.
    // If you're using this, you're probably starting to use MdcScope outside of container labelling.
    // If so, consider changing the defaults / builder / naming.
    public Builder setSimple(final boolean simple) {
      this.simple = simple;

      return this;
    }

    public MdcScope build() {
      final Map<String, String> extraMdcEntries = new HashMap<>();

      maybeLogPrefix.ifPresent(logPrefix -> {
        final String potentiallyColoredLog = maybePrefixColor
            .map(color -> LoggingHelper.applyColor(color, logPrefix))
            .orElse(logPrefix);

        extraMdcEntries.put(LoggingHelper.LOG_SOURCE_MDC_KEY, potentiallyColoredLog);

        if (simple) {
          // outputs much less information for this line. see log4j2.xml to see exactly what this does
          extraMdcEntries.put("simple", "true");
        }
      });

      return new MdcScope(extraMdcEntries);
    }

  }

}
