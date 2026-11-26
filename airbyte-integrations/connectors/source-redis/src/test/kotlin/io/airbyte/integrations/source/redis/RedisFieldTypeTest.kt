/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.read.StateManagerFactory
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.lang.reflect.Method
import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import sun.misc.Unsafe

class RedisFieldTypeTest {
    @Test
    fun testEveryCatalogFieldTypeRoundTripsThroughStateManagerFactory() {
        val factoryMethod: Method =
            StateManagerFactory::class
                .java
                .getDeclaredMethod(
                    "airbyteTypeFromJsonSchema",
                    JsonNode::class.java,
                )
                .apply { isAccessible = true }
        val stateManagerFactory: StateManagerFactory =
            unsafe().allocateInstance(StateManagerFactory::class.java) as StateManagerFactory
        val streamFactory = RedisAirbyteStreamFactory()
        val configuration =
            RedisSourceConfiguration(
                host = "localhost",
                port = 6379,
                username = null,
                password = null,
                database = 0,
                sslMode = RedisSslDisabled,
                keyPattern = "*",
                scanBatchSize = 1000,
                maxDbConnections = null,
                maxConcurrency = 1,
                realHost = "localhost",
                realPort = 6379,
                checkpointTargetInterval = Duration.ofSeconds(300),
                sshTunnel = SshNoTunnelMethod,
            )

        for (keyType in RedisKeyType.entries) {
            val id = StreamIdentifier.from(StreamDescriptor().withName(keyType.streamName))
            val discovered =
                DiscoveredStream(
                    id,
                    keyType.fields.map { EmittedField(it.name, it.type) },
                    keyType.primaryKey,
                )
            val stream = streamFactory.create(configuration, discovered)
            if (keyType.incremental) {
                Assertions.assertTrue(stream.sourceDefinedCursor)
                Assertions.assertEquals(listOf("id"), stream.defaultCursorField)
            } else {
                Assertions.assertNull(stream.sourceDefinedCursor)
                Assertions.assertNull(stream.defaultCursorField)
            }
            for (field in keyType.fields) {
                val fieldSchema = stream.jsonSchema["properties"][field.name]
                val derived =
                    factoryMethod.invoke(stateManagerFactory, fieldSchema) as AirbyteSchemaType
                Assertions.assertEquals(
                    field.type.airbyteSchemaType,
                    derived,
                    "${keyType.streamName}.${field.name}: ${Jsons.writeValueAsString(fieldSchema)}",
                )
            }
        }
    }

    private fun unsafe(): Unsafe {
        val field = Unsafe::class.java.getDeclaredField("theUnsafe")
        field.isAccessible = true
        return field.get(null) as Unsafe
    }
}
