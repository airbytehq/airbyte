/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Consumer
import java.util.function.Function

private val LOGGER = KotlinLogging.logger {}
/**
 * Multiple configs may allow you to sync data to the destination in multiple ways.
 *
 * One primary example is that the default behavior for some DB-based destinations may use
 * INSERT-based destinations while (given additional credentials) it may be able to sync data using
 * a file copied to a staging location.
 *
 * This class exists to make it easy to define a destination in terms of multiple other destination
 * implementations, switching between them based on the config provided.
 */
open class SwitchingDestination<T : Enum<T>>(
    enumClass: Class<T>,
    configToType: Function<JsonNode, T>,
    typeToDestination: Map<T, Destination>
) : BaseConnector(), Destination {
    private val configToType: Function<JsonNode, T>
    private val typeToDestination: Map<T, Destination>

    init {
        val allEnumConstants: Set<T> = HashSet(Arrays.asList(*enumClass.enumConstants))
        val supportedEnumConstants = typeToDestination.keys

        // check that it isn't possible for configToType to produce something we can't handle
        Preconditions.checkArgument(allEnumConstants == supportedEnumConstants)

        this.configToType = configToType
        this.typeToDestination = typeToDestination
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val destinationType = configToType.apply(config)
        LOGGER.info { "Using destination type: ${destinationType.name}" }
        return typeToDestination[destinationType]!!.check(config)
    }

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        val destinationType = configToType.apply(config)
        LOGGER.info { "Using destination type: ${destinationType.name}" }
        return typeToDestination[destinationType]!!.getConsumer(
            config,
            catalog,
            outputRecordCollector
        )
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer? {
        val destinationType = configToType.apply(config)
        LOGGER.info { "Using destination type: ${destinationType.name}" }
        return typeToDestination[destinationType]!!.getSerializedMessageConsumer(
            config,
            catalog,
            outputRecordCollector
        )
    }

    companion object {}
}
