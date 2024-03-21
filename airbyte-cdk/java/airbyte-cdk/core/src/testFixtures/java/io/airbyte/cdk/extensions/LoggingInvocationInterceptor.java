/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.extensions;

import static java.util.concurrent.TimeUnit.DAYS;
import static java.util.concurrent.TimeUnit.HOURS;
import static java.util.concurrent.TimeUnit.MICROSECONDS;
import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.concurrent.TimeUnit.MINUTES;
import static java.util.concurrent.TimeUnit.NANOSECONDS;
import static java.util.concurrent.TimeUnit.SECONDS;
import static java.util.regex.Pattern.CASE_INSENSITIVE;
import static java.util.regex.Pattern.UNICODE_CASE;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Proxy;
import java.time.Duration;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.commons.lang3.time.DurationFormatUtils;
import org.junit.jupiter.api.Timeout;
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

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingInvocationInterceptor.class);
  private static final String JUNIT_METHOD_EXECUTION_TIMEOUT_PROPERTY_NAME = "JunitMethodExecutionTimeout";

  private static final class LoggingInvocationInterceptorHandler implements InvocationHandler {

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
        logLineSuffix = "execution of @%s method %s.%s".formatted(interceptedEvent,
            invocationContext.getExecutable().getDeclaringClass().getSimpleName(),
            invocationContext.getExecutable().getName());
      } else {
        logLineSuffix = "execution of unknown intercepted call %s".formatted(methodName);
      }
      Thread currentThread = Thread.currentThread();
      TimeoutInteruptor timeoutTask = new TimeoutInteruptor(currentThread);
      Instant start = Instant.now();
      try {
        final Object retVal;
        Duration timeout = getTimeout(invocationContext);
        if (timeout != null) {
          LOGGER.info("Junit starting {} with timeout of {}", logLineSuffix, DurationFormatUtils.formatDurationWords(timeout.toMillis(), true, true));
          new Timer("TimeoutTimer-" + currentThread.getName(), true).schedule(timeoutTask, timeout.toMillis());
        } else {
          LOGGER.warn("Junit starting {} with no timeout", logLineSuffix);
        }
        retVal = invocation.proceed();
        long elapsedMs = Duration.between(start, Instant.now()).toMillis();
        LOGGER.info("Junit completed {} in {}", logLineSuffix, DurationFormatUtils.formatDurationWords(elapsedMs, true, true));
        return retVal;
      } catch (Throwable t) {
        timeoutTask.cancel();
        long elapsedMs = Duration.between(start, Instant.now()).toMillis();
        if (timeoutTask.wasTriggered) {
          Throwable t1 = t;
          t = new TimeoutException(
              "Execution was cancelled after %s. If you think your test should be given more time to complete, you can use the @Timeout annotation. If all the test of a connector are slow, "
                  + " you can override the property 'JunitMethodExecutionTimeout' in your gradle.properties."
                      .formatted(DurationFormatUtils.formatDurationWords(elapsedMs, true, true)));
          t.initCause(t1);
        }
        boolean belowCurrentCall = false;
        List<String> stackToDisplay = new LinkedList<>();
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
        LOGGER.error("Junit exception throw during {} after {}:\n{}", logLineSuffix, DurationFormatUtils.formatDurationWords(elapsedMs, true, true),
            stackTrace);
        throw t;
      } finally {
        timeoutTask.cancel();
      }
    }

    private static class TimeoutInteruptor extends TimerTask {

      private final Thread parentThread;
      volatile boolean wasTriggered = false;

      TimeoutInteruptor(Thread parentThread) {
        this.parentThread = parentThread;
      }

      @Override
      public void run() {
        wasTriggered = true;
        parentThread.interrupt();
      }

      public boolean cancel() {
        return super.cancel();
      }

    }

    private static final Pattern PATTERN = Pattern.compile("([1-9]\\d*) *((?:[nμm]?s)|m|h|d)?",
        CASE_INSENSITIVE | UNICODE_CASE);
    private static final Map<String, TimeUnit> UNITS_BY_ABBREVIATION;

    static {
      Map<String, TimeUnit> unitsByAbbreviation = new HashMap<>();
      unitsByAbbreviation.put("ns", NANOSECONDS);
      unitsByAbbreviation.put("μs", MICROSECONDS);
      unitsByAbbreviation.put("ms", MILLISECONDS);
      unitsByAbbreviation.put("s", SECONDS);
      unitsByAbbreviation.put("m", MINUTES);
      unitsByAbbreviation.put("h", HOURS);
      unitsByAbbreviation.put("d", DAYS);
      UNITS_BY_ABBREVIATION = Collections.unmodifiableMap(unitsByAbbreviation);
    }

    static Duration parseDuration(String text) throws DateTimeParseException {
      Matcher matcher = PATTERN.matcher(text.trim());
      if (matcher.matches()) {
        long value = Long.parseLong(matcher.group(1));
        String unitAbbreviation = matcher.group(2);
        TimeUnit unit = unitAbbreviation == null ? SECONDS
            : UNITS_BY_ABBREVIATION.get(unitAbbreviation.toLowerCase(Locale.ENGLISH));
        return Duration.ofSeconds(unit.toSeconds(value));
      }
      throw new DateTimeParseException("Timeout duration is not in the expected format (<number> [ns|μs|ms|s|m|h|d])",
          text, 0);
    }

    private static Duration getTimeout(ReflectiveInvocationContext<Method> invocationContext) {
      Duration timeout = null;
      if (invocationContext.getExecutable()instanceof Method m) {
        Timeout timeoutAnnotation = m.getAnnotation(Timeout.class);
        if (timeoutAnnotation == null) {
          timeoutAnnotation = invocationContext.getTargetClass().getAnnotation(Timeout.class);
        }
        if (timeoutAnnotation != null) {
          timeout = Duration.ofMillis(timeoutAnnotation.unit().toMillis(timeoutAnnotation.value()));
        }
      }
      if (timeout == null) {
        timeout = parseDuration(System.getProperty(JUNIT_METHOD_EXECUTION_TIMEOUT_PROPERTY_NAME));
      }
      return timeout;
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
    if (!Modifier.isPublic(invocationContext.getExecutable().getModifiers())) {
      LOGGER.warn("Junit method {}.{} is not declared as public", invocationContext.getExecutable().getDeclaringClass().getCanonicalName(),
          invocationContext.getExecutable().getName());
    }
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
