package io.airbyte.cdk.test.fixtures.legacy

import io.github.oshai.kotlinlogging.KotlinLogging
import org.slf4j.MDC
import java.io.BufferedReader
import java.io.ByteArrayInputStream
import java.io.IOException
import java.io.InputStream
import java.nio.charset.StandardCharsets
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}

class LineGobbler
@JvmOverloads
internal constructor(
    `is`: InputStream,
    private val consumer: Consumer<String>,
    private val executor: ExecutorService,
    private val mdc: Map<String?, String?>?,
    private val caller: String = GENERIC,
    private val containerLogMdcBuilder: MdcScope.Builder = MdcScope.Companion.DEFAULT_BUILDER
) : VoidCallable {
    private val `is`: BufferedReader = IOs.newBufferedReader(`is`)

    internal constructor(
        `is`: InputStream,
        consumer: Consumer<String>,
        executor: ExecutorService,
        mdc: Map<String?, String?>?,
        mdcScopeBuilder: MdcScope.Builder
    ) : this(`is`, consumer, executor, mdc, GENERIC, mdcScopeBuilder)

    override fun voidCall() {
        MDC.setContextMap(mdc)
        try {
            var line = `is`.readLine()
            while (line != null) {
                containerLogMdcBuilder.build().use { consumer.accept(line) }
                line = `is`.readLine()
            }
        } catch (i: IOException) {
            LOGGER.warn {
                "$caller gobbler IOException: ${i.message}. Typically happens when cancelling a job."
            }
        } catch (e: Exception) {
            LOGGER.error(e) { "$caller gobbler error when reading stream" }
        } finally {
            executor.shutdown()
        }
    }

    companion object {

        private const val GENERIC = "generic"

        @JvmOverloads
        fun gobble(
            message: String,
            consumer: Consumer<String> = Consumer { msg: String -> LOGGER.info { msg } }
        ) {
            val stringAsSteam: InputStream =
                ByteArrayInputStream(message.toByteArray(StandardCharsets.UTF_8))
            gobble(stringAsSteam, consumer)
        }

        /**
         * Used to emit a visual separator in the user-facing logs indicating a start of a
         * meaningful temporal activity
         *
         * @param message
         */
        fun startSection(message: String) {
            gobble("\r\n----- START $message -----\r\n\r\n")
        }

        /**
         * Used to emit a visual separator in the user-facing logs indicating a end of a meaningful
         * temporal activity
         *
         * @param message
         */
        fun endSection(message: String) {
            gobble("\r\n----- END $message -----\r\n\r\n")
        }

        fun gobble(
            `is`: InputStream,
            consumer: Consumer<String>,
            mdcScopeBuilder: MdcScope.Builder
        ) {
            gobble(`is`, consumer, GENERIC, mdcScopeBuilder)
        }

        @JvmOverloads
        fun gobble(
            `is`: InputStream,
            consumer: Consumer<String>,
            caller: String = GENERIC,
            mdcScopeBuilder: MdcScope.Builder = MdcScope.Companion.DEFAULT_BUILDER
        ) {
            val executor = Executors.newSingleThreadExecutor()
            val mdc = MDC.getCopyOfContextMap()
            val gobbler = LineGobbler(`is`, consumer, executor, mdc, caller, mdcScopeBuilder)
            executor.submit(gobbler)
        }
    }
}
