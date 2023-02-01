/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.argproviders.util;

import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import java.lang.reflect.Method;
import org.junit.jupiter.api.extension.ExtensionContext;

public class ArgumentProviderUtil {

  private static final String PROTOCOL_VERSION_METHOD_NAME = "getProtocolVersion";

  /**
   * This method use
   * {@link io.airbyte.integrations.standardtest.destination.ProtocolVersion#getPrefix()} to prefix
   * the file name.
   * <p>
   * example:
   * <p>
   * filename.json -> v0/filename.json
   *
   * @param fileName the original file name
   * @param protocolVersion supported protocol version
   * @return filename with protocol version prefix
   */
  public static String prefixFileNameByVersion(final String fileName, ProtocolVersion protocolVersion) {
    return String.format("%s/%s", protocolVersion.getPrefix(), fileName);
  }

  /**
   * This method use reflection to get protocol version method from provided test context.
   * <p>
   * NOTE: getProtocolVersion method should be public.
   *
   * @param context the context in which the current test is being executed.
   * @return supported protocol version
   */
  public static ProtocolVersion getProtocolVersion(ExtensionContext context) throws Exception {
    Class<?> c = context.getRequiredTestClass();
    // NOTE: Method should be public
    Method m = c.getMethod(PROTOCOL_VERSION_METHOD_NAME);
    return (ProtocolVersion) m.invoke(c.getDeclaredConstructor().newInstance());
  }

}
