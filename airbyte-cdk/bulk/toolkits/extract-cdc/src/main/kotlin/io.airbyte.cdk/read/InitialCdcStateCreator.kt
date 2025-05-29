/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.debezium.engine.spi.OffsetCommitPolicy
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/*
 Encapsulates logic for creating an initial cdc state. This could involve initialization steps
 such as building schema history & obtaining the initial offset.
*/
interface InitialCdcStateCreatorFactory {
    fun make(): OpaqueStateValue
}

@Singleton
class DefaultInitialCdcStateCreatorFactory(debeziumManager: DebeziumManager) :
    InitialCdcStateCreatorFactory {
    private val log = KotlinLogging.logger {}
    private val debeziumManager = debeziumManager
    private var engine: DebeziumEngine<ChangeEvent<String?, String?>>? = null

    override fun make(): OpaqueStateValue {
        engine = createDebeziumEngine()
        engine?.run()
        // Read state from files
        return this.debeziumManager.readOffsetState()
    }

    fun createDebeziumEngine(): DebeziumEngine<ChangeEvent<String?, String?>>? {
        log.info {
            "Using DBZ version: ${DebeziumEngine::class.java.getPackage().implementationVersion}"
        }
        return DebeziumEngine.create(Json::class.java)
            .using(this.debeziumManager.getPropertiesForSchemaHistory())
            .using(OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
            .notifying { event: ChangeEvent<String?, String?> ->
                if (event.value() == null) {
                    return@notifying
                }
                requestClose()
            }
            .using { success: Boolean, message: String?, error: Throwable? ->
                log.info { "Debezium engine shutdown. Engine terminated successfully : $success" }
                log.info { message }
                if (!success) {
                    if (error != null) {
                        log.info { "Debezium failed with: $error" }
                    } else {
                        // There are cases where Debezium doesn't succeed but only fills the
                        // message field.
                        // In that case, we still want to fail loud and clear
                        log.info { "Debezium failed with: $message" }
                    }
                }
            }
            .using(
                object : DebeziumEngine.ConnectorCallback {
                    override fun connectorStarted() {
                        log.info { "DebeziumEngine notify: connector started" }
                    }

                    override fun connectorStopped() {
                        log.info { "DebeziumEngine notify: connector stopped" }
                    }

                    override fun taskStarted() {
                        log.info { "DebeziumEngine notify: task started" }
                    }

                    override fun taskStopped() {
                        log.info { "DebeziumEngine notify: task stopped" }
                    }
                },
            )
            .build()
    }

    private fun requestClose() {
        log.info { "Closing schema history dbz run" }
        // TODO : send close analytics message
        // TODO : Close the engine. Note that engine must be closed in a different thread
        // than the running engine.
        CoroutineScope(Dispatchers.IO).launch { engine?.close() }
    }
}
