/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.workers.internal.AirbyteDestination
import java.nio.file.Path
import java.util.*

/**
 * Simple class to host a Destination in-memory rather than spinning up a container for it. For
 * debugging and testing purposes only; not recommended to use this for real code
 */
class LocalAirbyteDestination(private val dest: Destination) : AirbyteDestination {
    private var consumer: AirbyteMessageConsumer? = null
    private var isClosed = false

    @Throws(Exception::class)
    override fun start(
        destinationConfig: WorkerDestinationConfig,
        jobRoot: Path,
        additionalEnvironmentVariables: Map<String, String>
    ) {
        consumer =
            dest.getConsumer(
                destinationConfig.destinationConnectionConfiguration,
                Jsons.`object`(
                    Jsons.jsonNode(destinationConfig.catalog),
                    ConfiguredAirbyteCatalog::class.java
                )!!
            ) { Destination::defaultOutputRecordCollector }
        consumer!!.start()
    }

    @Throws(Exception::class)
    override fun accept(message: io.airbyte.protocol.models.AirbyteMessage) {
        consumer!!.accept(Jsons.`object`(Jsons.jsonNode(message), AirbyteMessage::class.java)!!)
    }

    override fun notifyEndOfInput() {
        // nothing to do here
    }

    @Throws(Exception::class)
    override fun close() {
        consumer!!.close()
        isClosed = true
    }

    override fun cancel() {
        // nothing to do here
    }

    override fun isFinished(): Boolean {
        return isClosed
    }

    override var exitValue = 0

    override fun attemptRead(): Optional<io.airbyte.protocol.models.AirbyteMessage> {
        return Optional.empty()
    }
}
