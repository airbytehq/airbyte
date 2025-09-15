/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.v0.AirbyteMessage

/**
 * Interface for the destination's consumption of incoming records wrapped in an
 * [io.airbyte.protocol.models.v0.AirbyteMessage].
 *
 * This is via the accept method, which commonly handles parsing, validation, batching and writing
 * of the transformed data to the final destination i.e. the technical system data is being written
 * to.
 *
 * Lifecycle:
 *
 * * 1. Instantiate consumer.
 * * 2. start() to initialize any resources that need to be created BEFORE the consumer consumes any
 * messages.
 * * 3. Consumes ALL records via [AirbyteMessageConsumer.accept]
 * * 4. Always (on success or failure) finalize by calling [AirbyteMessageConsumer.close]
 *
 * We encourage implementing this interface using the [FailureTrackingAirbyteMessageConsumer] class.
 */
interface AirbyteMessageConsumer : CheckedConsumer<AirbyteMessage, Exception>, AutoCloseable {
    @Throws(Exception::class) fun start()

    /**
     * Consumes all [AirbyteMessage]s
     *
     * @param message [AirbyteMessage] to be processed
     * @throws Exception
     */
    @Throws(Exception::class) override fun accept(message: AirbyteMessage)

    /**
     * Executes at the end of consumption of all incoming streamed data regardless of success or
     * failure
     *
     * @throws Exception
     */
    @Throws(Exception::class) override fun close()

    companion object {
        /** Append a function to be called on [AirbyteMessageConsumer.close]. */
        fun appendOnClose(
            consumer: AirbyteMessageConsumer?,
            voidCallable: VoidCallable
        ): AirbyteMessageConsumer {
            return object : AirbyteMessageConsumer {
                @Throws(Exception::class)
                override fun start() {
                    consumer!!.start()
                }

                @Throws(Exception::class)
                override fun accept(message: AirbyteMessage) {
                    consumer!!.accept(message)
                }

                @Throws(Exception::class)
                override fun close() {
                    consumer!!.close()
                    voidCallable.call()
                }
            }
        }
    }
}
