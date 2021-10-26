/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import java.util.Map;
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

}
