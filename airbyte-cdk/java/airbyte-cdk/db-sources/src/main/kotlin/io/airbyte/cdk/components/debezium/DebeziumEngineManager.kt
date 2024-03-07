/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.components.debezium

import io.airbyte.commons.json.Jsons
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.debezium.storage.file.history.FileSchemaHistory
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.source.SourceRecord
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.IOException
import java.io.UncheckedIOException
import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Method
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

class DebeziumEngineManager(
    @JvmField val input: DebeziumComponent.Input,
    private val stateFilesAccessor: StateFilesAccessor) {

    // Shared state.
    private val data = DebeziumEngineSharedState(input.config)

    // Engine running and stopping.
    private val engine: DebeziumEngine<ChangeEvent<String?, String?>>
    private val engineExecutor: ExecutorService = Executors.newSingleThreadExecutor { r: Runnable -> Thread(r, "debezium-engine-runner") }
    private val thrown = AtomicReference<Throwable>()
    private val isStopping = AtomicBoolean()
    private val stopperExecutor: ExecutorService = Executors.newSingleThreadExecutor { r: Runnable -> Thread(r, "debezium-engine-stopper") }

    init {
        val props = input.config.debeziumProperties.clone() as Properties
        props.setProperty(StandaloneConfig.OFFSET_STORAGE_FILE_FILENAME_CONFIG, stateFilesAccessor.offsetFilePath.toString())
        if (input.state.schema.isPresent) {
            props.setProperty(FileSchemaHistory.FILE_PATH.name(), stateFilesAccessor.schemaFilePath.toString())
        }
        this.engine = createDebeziumEngine(props)
    }

    private fun createDebeziumEngine(properties: Properties) : DebeziumEngine<ChangeEvent<String?, String?>> {
        return DebeziumEngine.create(Json::class.java)
                .using(properties)
                .notifying { event: ChangeEvent<String?, String?> -> onEvent(event) }
                .using { success: Boolean, message: String, error: Throwable? -> onCompletion(success, message, error) }
                .build()
    }

    private fun onEvent(event: ChangeEvent<String?, String?>) {
        if (event.value() == null) {
            // Debezium outputs a tombstone event that has a value of null. This is an artifact of how it
            // interacts with kafka. We want to ignore it. More on the tombstone:
            // https://debezium.io/documentation/reference/2.2/transformations/event-flattening.html
            return
        }
        // Deserialize the event value.
        val record = DebeziumComponent.Record(Jsons.deserialize(event.value()))
        // Try to get the SourceEvent object.
        val sourceRecord: SourceRecord? = maybeGetSourceRecord(event)
        // Update the shared state with the event.
        data.add(record, sourceRecord)
        // Check for completion.
        checkCompletion()
    }

    internal fun checkCompletion() {
        // If we're done, shut down engine, at most once.
        if (data.isComplete && isStopping.compareAndSet(false, true)) {
            // Shutting down the engine must be done in a different thread than the engine's run() method.
            // We're in the event callback right now, so that might be the current thread, we don't know.
            stopperExecutor.execute {
                try {
                    engine.close()
                } catch (e: IOException) {
                    // The close() method implementation in EmbeddedEngine is quite straightforward.
                    // It delegates to stop() and its contract is to be non-blocking.
                    // It doesn't throw any exceptions that we might want to act upon or propagate,
                    // but let's log them just in case.
                    LOGGER.warn("Exception thrown while stopping the Debezium engine.", e)
                } catch (e: RuntimeException) {
                    LOGGER.warn("Exception thrown while stopping the Debezium engine.", e)
                }
            }
        }
    }

    private fun maybeGetSourceRecord(event: ChangeEvent<String?, String?>): SourceRecord? {
        // Try to get the source record.
        if (EMBEDDED_ENGINE_CHANGE_EVENT.isInstance(event)) {
            try {
                val obj = SOURCE_RECORD_GETTER.invoke(event)
                if (obj is SourceRecord) {
                    return obj
                }
            } catch (e: IllegalAccessException) {
                LOGGER.debug("Failed to extract SourceRecord instance from Debezium ChangeEvent instance", e)
            } catch (e: InvocationTargetException) {
                LOGGER.debug("Failed to extract SourceRecord instance from Debezium ChangeEvent instance", e)
            }
        }
        return null
    }

    private fun onCompletion(success: Boolean, message: String?, error: Throwable?) {
        if (success) {
            LOGGER.info("Debezium engine has shut down successfully: {}", message)
            return
        }
        LOGGER.warn("Debezium engine has NOT shut down successfully: {}", message, error)
        // There are cases where Debezium doesn't succeed but only fills the message field.
        thrown.set(error ?: RuntimeException(message))
    }

    fun start(): DebeziumEngineManager {
        stateFilesAccessor.writeOffset(input.state.offset)
        input.state.schema.ifPresent { schema: DebeziumComponent.State.Schema -> stateFilesAccessor.writeSchema(schema) }
        data.reset()
        engineExecutor.execute(engine)
        return this
    }

    fun await(): DebeziumComponent.Output {
        // Wait for a predetermined amount of time for the Debezium engine to finish its execution.
        engineExecutor.shutdown()
        val engineHasShutDown: Boolean
        try {
            engineHasShutDown = engineExecutor.awaitTermination(input.config.maxTime.toMillis(), TimeUnit.MILLISECONDS)
        } catch (e: InterruptedException) {
            throw RuntimeException(e)
        }
        if (!engineHasShutDown) {
            // Engine hasn't shut down yet.
            // We've waited long enough: trigger the shutdown.
            data.addCompletionReason(DebeziumComponent.CompletionReason.HAS_COLLECTED_LONG_ENOUGH)
            try {
                engine.close()
            } catch (e: IOException) {
                throw UncheckedIOException(e)
            }
        }
        // At this point, the engine has either already shut down,
        // or the shut down has already been triggered.
        stopperExecutor.shutdown()
        stopperExecutor.close()
        engineExecutor.close()
        // Re-throw any exception.
        when (val throwable = thrown.get()) {
            null -> Unit
            is RuntimeException -> throw throwable
            else -> throw RuntimeException(throwable)
        }
        // Generate final state from file contents.
        val finalState = DebeziumComponent.State(
                stateFilesAccessor.readUpdatedOffset(input.state.offset),
                input.state.schema.map { _ -> stateFilesAccessor.readSchema() })
        return data.build(finalState)
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(DebeziumEngineManager::class.java)
        private val EMBEDDED_ENGINE_CHANGE_EVENT: Class<*>
        private val SOURCE_RECORD_GETTER: Method

        init {
            try {
                EMBEDDED_ENGINE_CHANGE_EVENT = Class.forName("io.debezium.embedded.EmbeddedEngineChangeEvent")
                SOURCE_RECORD_GETTER = EMBEDDED_ENGINE_CHANGE_EVENT.getDeclaredMethod("sourceRecord")
            } catch (e: ClassNotFoundException) {
                throw RuntimeException(e)
            } catch (e: NoSuchMethodException) {
                throw RuntimeException(e)
            }
            SOURCE_RECORD_GETTER.setAccessible(true)
        }

        @JvmStatic
        fun debeziumComponent(): DebeziumComponent {
            return DebeziumComponent { input: DebeziumComponent.Input ->
                StateFilesAccessor().use { stateFilesManager ->
                    return@DebeziumComponent DebeziumEngineManager(input, stateFilesManager).start().await()
                }
            }
        }
    }
}
