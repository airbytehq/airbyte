package io.airbyte.integrations.base.destination

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.temporal.ChronoUnit

private val logger = KotlinLogging.logger {}
abstract class IntegrationTest(
    val destinationFactory: DestinationFactory,
    val config: JsonNode,
) {
    abstract fun dumpRecords(): List<JsonNode>
    abstract fun dumpRawRecords(): List<JsonNode>

    fun runSync(
        catalog: ConfiguredAirbyteCatalog,
        messages: List<AirbyteMessage>,
    ) {
        val destination = destinationFactory.runDestination(
            Command.WRITE,
            config,
            catalog,
        )
        var destinationExited = false
        messages.forEach { inputMessage ->
            if (destinationExited) {
                throw IllegalStateException("Destination exited before it consumed all messages")
            }
            destination.sendMessage(inputMessage)
            destination.readMessages().forEach consumeDestinationOutput@ { outputMessage ->
                if (outputMessage == null) {
                    destinationExited = true
                    return@consumeDestinationOutput
                }
                // We could also e.g. capture state messages for verification
                if (outputMessage.type == AirbyteMessage.Type.LOG) {
                    logger.info { outputMessage.log.message }
                }
            }
        }
        while (true) {
            destination.readMessages().forEach { outputMessage ->
                if (outputMessage == null) {
                    return@forEach
                }
                if (outputMessage.type == AirbyteMessage.Type.LOG) {
                    logger.info { outputMessage.log.message }
                }
            }
            Thread.sleep(Duration.of(5, ChronoUnit.SECONDS))
        }
    }
}

interface Destination {
    fun sendMessage(message: AirbyteMessage)

    /**
     * Return all messages from the destination. When the destination exits, the last message
     * MUST be `null`.
     *
     * (mediocre interface, just for demo purposes)
     */
    fun readMessages(): List<AirbyteMessage?>

    fun waitUntilDone()
}

// we love factories, right? :D
// functional interface, so this can be invoked with just a lambda
fun interface DestinationFactory {
    fun runDestination(
        command: Command,
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
    ): Destination
}
