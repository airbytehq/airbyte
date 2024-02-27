/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.extensions;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.junit.jupiter.api.extension.DynamicTestInvocationContext;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.extension.InvocationInterceptor;
import org.junit.jupiter.api.extension.ReflectiveInvocationContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * By default, junit only output logs to the console, and nothing makes it into log4j logs. This
 * class fixes that by using the interceptor facility to print progress and timing information. This
 * allows us to have junit loglines in our test logs. This is instanciated via <a href=
 * "https://docs.oracle.com/javase%2F9%2Fdocs%2Fapi%2F%2F/java/util/ServiceLoader.html">Java's
 * ServiceLoader</a> The declaration can be found in
 * resources/META-INF/services/org.junit.jupiter.api.extension.Extension
 */
public class LoggingInvocationInterceptor implements InvocationInterceptor {

  private static final class LoggingInvocationInterceptorHandler implements InvocationHandler {

    private static final Logger LOGGER = LoggerFactory.getLogger(LoggingInvocationInterceptor.class);

    private static final Pattern methodPattern = Pattern.compile("intercept(.*)Method");

    @Override
    @SuppressWarnings("unchecked")
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
      if (LoggingInvocationInterceptor.class.getDeclaredMethod(method.getName(), Invocation.class, ReflectiveInvocationContext.class,
          ExtensionContext.class) == null) {
        LOGGER.error("Junit LoggingInvocationInterceptor executing unknown interception point {}", method.getName());
        return method.invoke(proxy, args);
      }
      var invocation = (Invocation<?>) args[0];
      var invocationContext = (ReflectiveInvocationContext<Method>) args[1];
      var extensionContext = (ExtensionContext) args[2];
      String methodName = method.getName();
      String logLineSuffix;
      Matcher methodMatcher = methodPattern.matcher(methodName);
      if (methodName.equals("interceptDynamicTest")) {
        logLineSuffix = "execution of DynamicTest %s".formatted(extensionContext.getDisplayName());
      } else if (methodName.equals("interceptTestClassConstructor")) {
        logLineSuffix = "instance creation for %s".formatted(invocationContext.getTargetClass());
      } else if (methodMatcher.matches()) {
        String interceptedEvent = methodMatcher.group(1);
        logLineSuffix = "execution of @%s method %s.%s".formatted(invocationContext.getExecutable().getDeclaringClass().getSimpleName(),
            interceptedEvent, invocationContext.getExecutable().getName());
      } else {
        logLineSuffix = "execution of unknown intercepted call %s".formatted(methodName);
      }
      LOGGER.info("Junit starting {}", logLineSuffix);
      try {
        Instant start = Instant.now();
        Object retVal = invocation.proceed();
        long elapsedMs = Duration.between(start, Instant.now()).toMillis();
        LOGGER.info("Junit completed {} in {} ms", logLineSuffix, elapsedMs);
        return retVal;
      } catch (Throwable t) {
        boolean belowCurrentCall = false;
        List<String> stackToDisplay = new LinkedList<String>();
        for (String stackString : ExceptionUtils.getStackFrames(t)) {
          if (stackString.startsWith("\tat ")) {
            if (!belowCurrentCall && stackString.contains(LoggingInvocationInterceptor.class.getCanonicalName())) {
              belowCurrentCall = true;
            }
          } else {
            belowCurrentCall = false;
          }
          if (!belowCurrentCall) {
            stackToDisplay.add(stackString);
          }
        }
        String stackTrace = StringUtils.join(stackToDisplay, "\n    ");
        LOGGER.warn("Junit exception throw during {}:\n{}", logLineSuffix, stackTrace);
        throw t;
      }
    }

  }

  private final InvocationInterceptor proxy = (InvocationInterceptor) Proxy.newProxyInstance(
      getClass().getClassLoader(),
      new Class[] {InvocationInterceptor.class},
      new LoggingInvocationInterceptorHandler());

  @Override
  public void interceptAfterAllMethod(Invocation<Void> invocation,
                                      ReflectiveInvocationContext<Method> invocationContext,
                                      ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptAfterAllMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public void interceptAfterEachMethod(Invocation<Void> invocation,
                                       ReflectiveInvocationContext<Method> invocationContext,
                                       ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptAfterEachMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public void interceptBeforeAllMethod(Invocation<Void> invocation,
                                       ReflectiveInvocationContext<Method> invocationContext,
                                       ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptBeforeAllMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public void interceptBeforeEachMethod(Invocation<Void> invocation,
                                        ReflectiveInvocationContext<Method> invocationContext,
                                        ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptBeforeEachMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public void interceptDynamicTest(Invocation<Void> invocation,
                                   DynamicTestInvocationContext invocationContext,
                                   ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptDynamicTest(invocation, invocationContext, extensionContext);
  }

  @Override
  public void interceptTestMethod(Invocation<Void> invocation,
                                  ReflectiveInvocationContext<Method> invocationContext,
                                  ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptTestMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public void interceptTestTemplateMethod(Invocation<Void> invocation,
                                          ReflectiveInvocationContext<Method> invocationContext,
                                          ExtensionContext extensionContext)
      throws Throwable {
    proxy.interceptTestTemplateMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public <T> T interceptTestFactoryMethod(Invocation<T> invocation,
                                          ReflectiveInvocationContext<Method> invocationContext,
                                          ExtensionContext extensionContext)
      throws Throwable {
    return proxy.interceptTestFactoryMethod(invocation, invocationContext, extensionContext);
  }

  @Override
  public <T> T interceptTestClassConstructor(Invocation<T> invocation,
                                             ReflectiveInvocationContext<Constructor<T>> invocationContext,
                                             ExtensionContext extensionContext)
      throws Throwable {
    return proxy.interceptTestClassConstructor(invocation, invocationContext, extensionContext);
  }

}
