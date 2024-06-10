/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.extensions

import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.reflect.*
import java.time.Duration
import java.time.Instant
import java.time.format.DateTimeParseException
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException
import java.util.regex.Pattern
import kotlin.concurrent.Volatile
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.exception.ExceptionUtils
import org.apache.commons.lang3.time.DurationFormatUtils
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.extension.DynamicTestInvocationContext
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.api.extension.InvocationInterceptor
import org.junit.jupiter.api.extension.ReflectiveInvocationContext

private val LOGGER = KotlinLogging.logger {}
/**
 * By default, junit only output logs to the console, and nothing makes it into log4j logs. This
 * class fixes that by using the interceptor facility to print progress and timing information. This
 * allows us to have junit loglines in our test logs. This is instanciated via
 * [Java's
 * ServiceLoader](https://docs.oracle.com/javase%2F9%2Fdocs%2Fapi%2F%2F/java/util/ServiceLoader.html)
 * The declaration can be found in
 * resources/META-INF/services/org.junit.jupiter.api.extension.Extension
 */
class LoggingInvocationInterceptor : InvocationInterceptor {
    private class LoggingInvocationInterceptorHandler : InvocationHandler {
        @Throws(Throwable::class)
        override fun invoke(proxy: Any, method: Method, args: Array<Any>): Any? {
            val methodName = method.name
            val invocationContextClass: Class<*> =
                when (methodName) {
                    "interceptDynamicTest" -> DynamicTestInvocationContext::class.java
                    else -> ReflectiveInvocationContext::class.java
                }
            try {
                LoggingInvocationInterceptor::class
                    .java
                    .getDeclaredMethod(
                        method.name,
                        InvocationInterceptor.Invocation::class.java,
                        invocationContextClass,
                        ExtensionContext::class.java
                    )
            } catch (_: NoSuchMethodException) {
                LOGGER.error(
                    "Junit LoggingInvocationInterceptor executing unknown interception point {}",
                    method.name
                )
                return method.invoke(proxy, *(args))
            }
            val invocation = args[0] as InvocationInterceptor.Invocation<*>?
            val reflectiveInvocationContext = args[1] as? ReflectiveInvocationContext<*>
            val extensionContext = args[2] as ExtensionContext?
            val logLineSuffix: String
            val methodMatcher = methodPattern.matcher(methodName)
            if (methodName == "interceptDynamicTest") {
                logLineSuffix = "execution of DynamicTest ${extensionContext!!.displayName}"
            } else if (methodName == "interceptTestClassConstructor") {
                logLineSuffix =
                    "instance creation for %s".formatted(reflectiveInvocationContext!!.targetClass)
            } else if (methodMatcher.matches()) {
                val interceptedEvent = methodMatcher.group(1)
                val methodRealClassName =
                    reflectiveInvocationContext!!.executable!!.declaringClass.simpleName
                val methodName = reflectiveInvocationContext.executable!!.name
                val targetClassName = reflectiveInvocationContext.targetClass.simpleName
                val methodDisplayName =
                    if (targetClassName == methodRealClassName) methodName
                    else "$methodName($methodRealClassName)"
                logLineSuffix =
                    "execution of @%s method %s.%s".formatted(
                        interceptedEvent,
                        targetClassName,
                        methodDisplayName
                    )
                TestContext.CURRENT_TEST_NAME.set("$targetClassName.$methodName")
            } else {
                logLineSuffix = "execution of unknown intercepted call $methodName"
            }
            val currentThread = Thread.currentThread()
            val timeoutTask = TimeoutInteruptor(currentThread)
            val start = Instant.now()
            try {
                val timeout = reflectiveInvocationContext?.let(::getTimeout)
                if (timeout != null) {
                    LOGGER.info(
                        "Junit starting {} with timeout of {}",
                        logLineSuffix,
                        DurationFormatUtils.formatDurationWords(timeout.toMillis(), true, true)
                    )
                    Timer("TimeoutTimer-" + currentThread.name, true)
                        .schedule(timeoutTask, timeout.toMillis())
                } else {
                    LOGGER.warn("Junit starting {} with no timeout", logLineSuffix)
                }
                val retVal = invocation!!.proceed()
                val elapsedMs = Duration.between(start, Instant.now()).toMillis()
                LOGGER.info(
                    "Junit completed {} in {}",
                    logLineSuffix,
                    DurationFormatUtils.formatDurationWords(elapsedMs, true, true)
                )
                return retVal
            } catch (throwable: Throwable) {
                timeoutTask.cancel()
                val elapsedMs = Duration.between(start, Instant.now()).toMillis()
                val t1: Throwable
                if (timeoutTask.wasTriggered) {
                    val timeoutAsString =
                        DurationFormatUtils.formatDurationWords(elapsedMs, true, true)
                    t1 =
                        TimeoutException(
                            "Execution was cancelled after $timeoutAsString. If you think your test should be given more time to complete, " +
                                "you can use the @Timeout annotation. If all the test of a connector are slow, " +
                                " you can override the property 'JunitMethodExecutionTimeout' in your gradle.properties."
                        )
                    t1.initCause(throwable)
                } else {
                    t1 = throwable
                }
                var belowCurrentCall = false
                val stackToDisplay: MutableList<String> = LinkedList()
                for (stackString in ExceptionUtils.getStackFrames(throwable)) {
                    if (stackString!!.startsWith("\tat ")) {
                        if (
                            !belowCurrentCall &&
                                stackString.contains(
                                    LoggingInvocationInterceptor::class.java.canonicalName
                                )
                        ) {
                            belowCurrentCall = true
                        }
                    } else {
                        belowCurrentCall = false
                    }
                    if (!belowCurrentCall) {
                        stackToDisplay.add(stackString)
                    }
                }
                val stackTrace = StringUtils.join(stackToDisplay, "\n    ")
                LOGGER.error(
                    "Junit exception throw during {} after {}:\n{}",
                    logLineSuffix,
                    DurationFormatUtils.formatDurationWords(elapsedMs, true, true),
                    stackTrace
                )
                throw t1
            } finally {
                timeoutTask.cancel()
                TestContext.CURRENT_TEST_NAME.set(null)
            }
        }

        private class TimeoutInteruptor(private val parentThread: Thread) : TimerTask() {
            @Volatile var wasTriggered: Boolean = false

            override fun run() {
                LOGGER.info(
                    "interrupting running task on ${parentThread.name}. Current Stacktrace is ${parentThread.stackTrace.asList()}"
                )
                wasTriggered = true
                parentThread.interrupt()
            }

            override fun cancel(): Boolean {
                LOGGER.info("cancelling timer task on ${parentThread.name}")
                return super.cancel()
            }
        }

        companion object {
            private val methodPattern: Pattern = Pattern.compile("intercept(.*)Method")

            private val PATTERN: Pattern =
                Pattern.compile(
                    "([1-9]\\d*) *((?:[nμm]?s)|m|h|d)?",
                    Pattern.CASE_INSENSITIVE or Pattern.UNICODE_CASE
                )
            private val UNITS_BY_ABBREVIATION: MutableMap<String, TimeUnit>

            init {
                val unitsByAbbreviation: MutableMap<String, TimeUnit> = HashMap()
                unitsByAbbreviation["ns"] = TimeUnit.NANOSECONDS
                unitsByAbbreviation["μs"] = TimeUnit.MICROSECONDS
                unitsByAbbreviation["ms"] = TimeUnit.MILLISECONDS
                unitsByAbbreviation["s"] = TimeUnit.SECONDS
                unitsByAbbreviation["m"] = TimeUnit.MINUTES
                unitsByAbbreviation["h"] = TimeUnit.HOURS
                unitsByAbbreviation["d"] = TimeUnit.DAYS
                UNITS_BY_ABBREVIATION = Collections.unmodifiableMap(unitsByAbbreviation)
            }

            @Throws(DateTimeParseException::class)
            fun parseDuration(text: String): Duration {
                val matcher = PATTERN.matcher(text.trim { it <= ' ' })
                if (matcher.matches()) {
                    val value = matcher.group(1).toLong()
                    val unitAbbreviation = matcher.group(2)
                    val unit =
                        if (unitAbbreviation == null) TimeUnit.SECONDS
                        else UNITS_BY_ABBREVIATION.getValue(unitAbbreviation.lowercase())
                    return Duration.ofSeconds(unit.toSeconds(value))
                }
                throw DateTimeParseException(
                    "Timeout duration is not in the expected format (<number> [ns|μs|ms|s|m|h|d])",
                    text,
                    0
                )
            }

            private fun getTimeout(invocationContext: ReflectiveInvocationContext<*>): Duration {
                var timeout: Duration? = null
                var m = invocationContext.executable
                if (m is Method) {
                    var timeoutAnnotation: Timeout? = m.getAnnotation(Timeout::class.java)
                    if (timeoutAnnotation == null) {
                        timeoutAnnotation =
                            invocationContext.targetClass.getAnnotation(Timeout::class.java)
                    }
                    if (timeoutAnnotation != null) {
                        timeout =
                            Duration.ofMillis(
                                timeoutAnnotation.unit.toMillis(timeoutAnnotation.value)
                            )
                    }
                }
                if (timeout == null) {
                    timeout =
                        parseDuration(
                            System.getProperty(JUNIT_METHOD_EXECUTION_TIMEOUT_PROPERTY_NAME)
                        )
                }
                return timeout
            }
        }
    }

    private val proxy: InvocationInterceptor? =
        Proxy.newProxyInstance(
            javaClass.classLoader,
            arrayOf<Class<*>?>(InvocationInterceptor::class.java),
            LoggingInvocationInterceptorHandler()
        ) as InvocationInterceptor

    @Throws(Throwable::class)
    override fun interceptAfterAllMethod(
        invocation: InvocationInterceptor.Invocation<Void>?,
        invocationContext: ReflectiveInvocationContext<Method>?,
        extensionContext: ExtensionContext?
    ) {
        proxy!!.interceptAfterAllMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun interceptAfterEachMethod(
        invocation: InvocationInterceptor.Invocation<Void>?,
        invocationContext: ReflectiveInvocationContext<Method>?,
        extensionContext: ExtensionContext?
    ) {
        proxy!!.interceptAfterEachMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun interceptBeforeAllMethod(
        invocation: InvocationInterceptor.Invocation<Void>?,
        invocationContext: ReflectiveInvocationContext<Method>?,
        extensionContext: ExtensionContext?
    ) {
        proxy!!.interceptBeforeAllMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun interceptBeforeEachMethod(
        invocation: InvocationInterceptor.Invocation<Void>?,
        invocationContext: ReflectiveInvocationContext<Method>?,
        extensionContext: ExtensionContext?
    ) {
        proxy!!.interceptBeforeEachMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun interceptDynamicTest(
        invocation: InvocationInterceptor.Invocation<Void>?,
        invocationContext: DynamicTestInvocationContext?,
        extensionContext: ExtensionContext?
    ) {
        proxy!!.interceptDynamicTest(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun interceptTestMethod(
        invocation: InvocationInterceptor.Invocation<Void>,
        invocationContext: ReflectiveInvocationContext<Method>,
        extensionContext: ExtensionContext
    ) {
        if (!Modifier.isPublic(invocationContext.executable!!.modifiers)) {
            LOGGER!!.warn(
                "Junit method {}.{} is not declared as public",
                invocationContext.executable!!.declaringClass.canonicalName,
                invocationContext.executable!!.name
            )
        }
        proxy!!.interceptTestMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun interceptTestTemplateMethod(
        invocation: InvocationInterceptor.Invocation<Void>?,
        invocationContext: ReflectiveInvocationContext<Method>?,
        extensionContext: ExtensionContext?
    ) {
        proxy!!.interceptTestTemplateMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun <T> interceptTestFactoryMethod(
        invocation: InvocationInterceptor.Invocation<T>?,
        invocationContext: ReflectiveInvocationContext<Method>?,
        extensionContext: ExtensionContext?
    ): T? {
        return proxy!!.interceptTestFactoryMethod(invocation, invocationContext, extensionContext)
    }

    @Throws(Throwable::class)
    override fun <T> interceptTestClassConstructor(
        invocation: InvocationInterceptor.Invocation<T>?,
        invocationContext: ReflectiveInvocationContext<Constructor<T>?>?,
        extensionContext: ExtensionContext?
    ): T? {
        return proxy!!.interceptTestClassConstructor(
            invocation,
            invocationContext,
            extensionContext
        )
    }

    companion object {
        private val JUNIT_METHOD_EXECUTION_TIMEOUT_PROPERTY_NAME: String =
            "JunitMethodExecutionTimeout"
    }
}
