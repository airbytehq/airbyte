/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

/**
 * Interface for the destination's consumption of incoming messages as strings. This interface is
 * backwards compatible with [AirbyteMessageConsumer].
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
 * * 3. Consumes ALL records via [SerializedAirbyteMessageConsumer.accept]
 * * 4. Always (on success or failure) finalize by calling [SerializedAirbyteMessageConsumer.close]
 */
interface SerializedAirbyteMessageConsumer :
    CheckedBiConsumer<String, Int, Exception>, AutoCloseable {
    /**
     * Initialize anything needed for the consumer. Must be called before accept.
     *
     * @throws Exception exception
     */
    @Throws(Exception::class) fun start()

    /**
     * Consumes all [AirbyteMessage]s
     *
     * @param message [AirbyteMessage] as a string
     * @param sizeInBytes size of that string in bytes
     * @throws Exception exception
     */
    @Throws(Exception::class) override fun accept(message: String, sizeInBytes: Int)

    /**
     * Executes at the end of consumption of all incoming streamed data regardless of success or
     * failure
     *
     * @throws Exception exception
     */
    @Throws(Exception::class) override fun close()

    companion object {
        /** Append a function to be called on [SerializedAirbyteMessageConsumer.close]. */
        fun appendOnClose(
            consumer: SerializedAirbyteMessageConsumer?,
            voidCallable: VoidCallable
        ): SerializedAirbyteMessageConsumer {
            return object : SerializedAirbyteMessageConsumer {
                @Throws(Exception::class)
                override fun start() {
                    consumer!!.start()
                }

                @Throws(Exception::class)
                override fun accept(message: String, sizeInBytes: Int) {
                    consumer!!.accept(message, sizeInBytes)
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
