/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import io.airbyte.protocol.models.v0.AirbyteMessage
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Minimal abstract class intended to provide a consistent structure to classes seeking to implement
 * the [AirbyteMessageConsumer] interface. The original interface methods are wrapped in generic
 * exception handlers - any exception is caught and logged.
 *
 * Two methods are intended for extension:
 *
 * * startTracked: Wraps set up of necessary infrastructure/configuration before message
 * consumption.
 * * acceptTracked: Wraps actual processing of each [io.airbyte.protocol.models.v0.AirbyteMessage].
 *
 * Though not necessary, we highly encourage using this class when implementing destinations. See
 * child classes for examples.
 */
abstract class FailureTrackingAirbyteMessageConsumer : AirbyteMessageConsumer {
    private var hasFailed = false

    /**
     * Wraps setup of necessary infrastructure/configuration before message consumption
     *
     * @throws Exception
     */
    @Throws(Exception::class) protected abstract fun startTracked()

    @Throws(Exception::class)
    override fun start() {
        try {
            startTracked()
        } catch (e: Exception) {
            LOGGER.error("Exception while starting consumer", e)
            hasFailed = true
            throw e
        }
    }

    /**
     * Processing of AirbyteMessages with general functionality of storing STATE messages,
     * serializing RECORD messages and storage within a buffer
     *
     * NOTE: Not all the functionality mentioned above is always true but generally applies
     *
     * @param msg [AirbyteMessage] to be processed
     * @throws Exception
     */
    @Throws(Exception::class) protected abstract fun acceptTracked(msg: AirbyteMessage)

    @Throws(Exception::class)
    override fun accept(msg: AirbyteMessage) {
        try {
            acceptTracked(msg)
        } catch (e: Exception) {
            LOGGER.error("Exception while accepting message", e)
            hasFailed = true
            throw e
        }
    }

    @Throws(Exception::class) protected abstract fun close(hasFailed: Boolean)

    @Throws(Exception::class)
    override fun close() {
        if (hasFailed) {
            LOGGER.warn("Airbyte message consumer: failed.")
        } else {
            LOGGER.info("Airbyte message consumer: succeeded.")
        }
        close(hasFailed)
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(FailureTrackingAirbyteMessageConsumer::class.java)
    }
}
