package io.airbyte.integrations.base.destination.typing_deduping

import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Extends all classes to lazily initialize a Slf4j [Logger]
 */
fun <R: Any> R.logger(): Lazy<Logger> {
    return lazy { LoggerFactory.getLogger(this.javaClass) }
}
