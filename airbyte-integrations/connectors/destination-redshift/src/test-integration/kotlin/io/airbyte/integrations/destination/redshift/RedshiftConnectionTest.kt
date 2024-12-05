/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class RedshiftConnectionTest {
    private val config = deserialize(readFile(Path.of("secrets/config_staging.json")))
    private val destination = RedshiftDestination()
    private var status: AirbyteConnectionStatus? = null

    @Test
    @Throws(Exception::class)
    fun testCheckIncorrectPasswordFailure() {
        (config as ObjectNode).put("password", "fake")
        DestinationConfig.initialize(config)
        status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status!!.message.contains("State code: 28000;"))
    }

    @Test
    @Throws(Exception::class)
    fun testCheckIncorrectUsernameFailure() {
        (config as ObjectNode).put("username", "")
        DestinationConfig.initialize(config)
        status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status!!.message.contains("State code: 28000;"))
    }

    @Test
    @Throws(Exception::class)
    fun testCheckIncorrectHostFailure() {
        (config as ObjectNode).put("host", "localhost2")
        DestinationConfig.initialize(config)
        status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status!!.message.contains("State code: 08001;"))
    }

    @Test
    @Throws(Exception::class)
    fun testCheckIncorrectDataBaseFailure() {
        (config as ObjectNode).put("database", "wrongdatabase")
        DestinationConfig.initialize(config)
        status = destination.check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status!!.message.contains("State code: 3D000;"))
    }
}
