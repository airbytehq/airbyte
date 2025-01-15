package io.airbyte.integrations.source.mydb

import io.airbyte.cdk.AirbyteSourceRunner

object MyDbSource {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteSoureRunner.run(*args)
    }
}
