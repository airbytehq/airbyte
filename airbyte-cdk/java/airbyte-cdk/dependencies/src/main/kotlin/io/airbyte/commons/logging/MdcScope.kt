/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.logging

import java.util.*
import java.util.function.BiConsumer
import org.slf4j.MDC

/**
 * This class is an autoClosable class that will add some specific values into the log MDC. When
 * being close, it will restore the original MDC. It is advised to use it like that:
 *
 * <pre> ` try(final ScopedMDCChange scopedMDCChange = new ScopedMDCChange( new HashMap<String,
 * String>() {{ put("my", "value"); }} )) { ... } ` * </pre> *
 */
class MdcScope(keyValuesToAdd: Map<String, String>) : AutoCloseable {
    private val originalContextMap: Map<String, String> = MDC.getCopyOfContextMap()

    init {
        keyValuesToAdd.forEach { (key: String?, `val`: String?) -> MDC.put(key, `val`) }
    }

    override fun close() {
        MDC.setContextMap(originalContextMap)
    }

    class Builder {
        private var maybeLogPrefix = Optional.empty<String>()
        private var maybePrefixColor = Optional.empty<LoggingHelper.Color>()
        private var simple = true

        fun setLogPrefix(logPrefix: String?): Builder {
            this.maybeLogPrefix = Optional.ofNullable(logPrefix)

            return this
        }

        fun setPrefixColor(color: LoggingHelper.Color?): Builder {
            this.maybePrefixColor = Optional.ofNullable(color)

            return this
        }

        // Use this to disable simple logging for things in an MdcScope.
        // If you're using this, you're probably starting to use MdcScope outside of container
        // labelling.
        // If so, consider changing the defaults / builder / naming.
        fun setSimple(simple: Boolean): Builder {
            this.simple = simple

            return this
        }

        fun produceMappings(mdcConsumer: BiConsumer<String, String>) {
            maybeLogPrefix.ifPresent { logPrefix: String ->
                val potentiallyColoredLog =
                    maybePrefixColor
                        .map { color: LoggingHelper.Color ->
                            LoggingHelper.applyColor(color, logPrefix)
                        }
                        .orElse(logPrefix)
                mdcConsumer.accept(LoggingHelper.LOG_SOURCE_MDC_KEY, potentiallyColoredLog)
                if (simple) {
                    // outputs much less information for this line. see log4j2.xml to see exactly
                    // what this does
                    mdcConsumer.accept("simple", "true")
                }
            }
        }

        fun build(): MdcScope {
            val extraMdcEntries: MutableMap<String, String> = HashMap()
            produceMappings { key: String, value: String -> extraMdcEntries[key] = value }
            return MdcScope(extraMdcEntries)
        }
    }

    companion object {
        val DEFAULT_BUILDER: Builder = Builder()
    }
}
